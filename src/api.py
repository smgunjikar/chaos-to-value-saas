"""
FastAPI web interface for the AI Social Media Agent
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from loguru import logger

from .ai_agent import AISocialMediaAgent
from .models import Platform, PostStatus, AgentStatus, PostingMetrics
from .config import config


# Create FastAPI app
app = FastAPI(
    title="AI Social Media Agent API",
    description="API for monitoring and controlling the 24/7 AI social media posting agent",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
agent: Optional[AISocialMediaAgent] = None


class ManualPostRequest(BaseModel):
    """Request model for manual posting"""
    platform: Platform
    content: str
    include_media: bool = False


class PostingScheduleRequest(BaseModel):
    """Request model for posting schedule"""
    platform: Platform
    frequency: str  # "hourly", "daily", "weekly", "custom"
    interval_minutes: int = 60
    start_time: datetime
    end_time: Optional[datetime] = None
    content_types: List[str] = ["text"]
    topics: Optional[List[str]] = None


@app.on_event("startup")
async def startup_event():
    """Initialize the AI agent on startup"""
    global agent
    agent = AISocialMediaAgent()
    logger.info("AI Social Media Agent initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global agent
    if agent:
        await agent.stop()
        logger.info("AI Social Media Agent stopped")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Social Media Agent API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    global agent
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        status = await agent.get_status()
        return {
            "status": "healthy",
            "agent_running": status.is_running,
            "active_platforms": len(status.active_platforms),
            "uptime": status.uptime
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/status")
async def get_agent_status():
    """Get detailed agent status"""
    global agent
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        status = await agent.get_status()
        return status.dict()
    except Exception as e:
        logger.error(f"Failed to get agent status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/start")
async def start_agent(background_tasks: BackgroundTasks):
    """Start the AI agent"""
    global agent
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    if agent.is_running:
        return {"message": "Agent is already running"}
    
    try:
        background_tasks.add_task(agent.start)
        return {"message": "Agent started successfully"}
    except Exception as e:
        logger.error(f"Failed to start agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/stop")
async def stop_agent():
    """Stop the AI agent"""
    global agent
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    if not agent.is_running:
        return {"message": "Agent is not running"}
    
    try:
        await agent.stop()
        return {"message": "Agent stopped successfully"}
    except Exception as e:
        logger.error(f"Failed to stop agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/platforms")
async def get_platforms():
    """Get list of configured platforms"""
    global agent
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    platforms = []
    for platform_name, platform_instance in agent.platforms.items():
        platforms.append({
            "platform": platform_name.value,
            "connected": platform_instance.is_connected,
            "status": "active" if platform_instance.is_connected else "inactive"
        })
    
    return {"platforms": platforms}


@app.get("/platforms/{platform}/health")
async def get_platform_health(platform: str):
    """Get health status of a specific platform"""
    global agent
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        platform_enum = Platform(platform)
        if platform_enum not in agent.platforms:
            raise HTTPException(status_code=404, detail=f"Platform {platform} not configured")
        
        platform_instance = agent.platforms[platform_enum]
        health = await platform_instance.health_check()
        return health
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid platform: {platform}")
    except Exception as e:
        logger.error(f"Failed to get platform health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/post/manual")
async def manual_post(request: ManualPostRequest):
    """Manually post content to a specific platform"""
    global agent
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        result = await agent.manual_post(
            platform=request.platform,
            content=request.content,
            include_media=request.include_media
        )
        return result
    except Exception as e:
        logger.error(f"Manual post failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/posts")
async def get_posts(
    platform: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Get posting history"""
    global agent
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        posts = agent.posting_history
        
        # Filter by platform
        if platform:
            try:
                platform_enum = Platform(platform)
                posts = [p for p in posts if p.platform == platform_enum]
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid platform: {platform}")
        
        # Filter by status
        if status:
            try:
                status_enum = PostStatus(status)
                posts = [p for p in posts if p.status == status_enum]
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
        
        # Sort by creation time (newest first)
        posts.sort(key=lambda x: x.created_at, reverse=True)
        
        # Paginate
        posts = posts[offset:offset + limit]
        
        return {
            "posts": [post.dict() for post in posts],
            "total": len(agent.posting_history),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Failed to get posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
async def get_metrics(days: int = 7):
    """Get posting metrics"""
    global agent
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        metrics = await agent.get_posting_metrics(days=days)
        return {
            "metrics": {k: v.dict() for k, v in metrics.items()},
            "period_days": days
        }
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics")
async def get_analytics():
    """Get analytics data"""
    global agent
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        # Calculate analytics
        total_posts = len(agent.posting_history)
        successful_posts = len([p for p in agent.posting_history if p.status == PostStatus.POSTED])
        failed_posts = len([p for p in agent.posting_history if p.status == PostStatus.FAILED])
        
        # Calculate engagement metrics
        total_engagement = 0
        for post in agent.posting_history:
            if post.engagement_metrics:
                total_engagement += (
                    post.engagement_metrics.get("likes", 0) +
                    post.engagement_metrics.get("shares", 0) +
                    post.engagement_metrics.get("comments", 0)
                )
        
        # Platform breakdown
        platform_stats = {}
        for platform in Platform:
            platform_posts = [p for p in agent.posting_history if p.platform == platform]
            if platform_posts:
                platform_stats[platform.value] = {
                    "total_posts": len(platform_posts),
                    "successful_posts": len([p for p in platform_posts if p.status == PostStatus.POSTED]),
                    "failed_posts": len([p for p in platform_posts if p.status == PostStatus.FAILED])
                }
        
        return {
            "total_posts": total_posts,
            "successful_posts": successful_posts,
            "failed_posts": failed_posts,
            "success_rate": (successful_posts / total_posts * 100) if total_posts > 0 else 0,
            "total_engagement": total_engagement,
            "platform_stats": platform_stats,
            "agent_status": await agent.get_status()
        }
    except Exception as e:
        logger.error(f"Failed to get analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/config")
async def get_config():
    """Get current configuration"""
    return {
        "environment": config.environment,
        "debug": config.debug,
        "scheduling": {
            "min_interval": config.scheduling.min_interval,
            "max_interval": config.scheduling.max_interval,
            "posting_start_hour": config.scheduling.posting_start_hour,
            "posting_end_hour": config.scheduling.posting_end_hour,
            "max_daily_posts": config.scheduling.max_daily_posts
        },
        "ai": {
            "openai_model": config.ai.openai_model,
            "anthropic_model": config.ai.anthropic_model,
            "max_hashtags": config.ai.max_hashtags
        },
        "monitoring": {
            "log_level": config.monitoring.log_level,
            "enable_metrics": config.monitoring.enable_metrics
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""
Main AI Agent for 24/7 Social Media Posting
"""

import asyncio
import random
import schedule
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from loguru import logger

from .config import config
from .ai_content_generator import AIContentGenerator
from .models import (
    Platform, ContentRequest, GeneratedContent, SocialMediaPost, 
    PostStatus, PlatformCredentials, AgentStatus, PostingMetrics
)
from .platforms import (
    TwitterPlatform, FacebookPlatform, LinkedInPlatform, 
    InstagramPlatform, PinterestPlatform
)


class AISocialMediaAgent:
    """Main AI agent for 24/7 social media posting"""
    
    def __init__(self):
        self.content_generator = AIContentGenerator()
        self.platforms: Dict[Platform, Any] = {}
        self.is_running = False
        self.status = AgentStatus()
        self.posting_history: List[SocialMediaPost] = []
        self.metrics: Dict[str, PostingMetrics] = {}
        
        self._setup_platforms()
        self._setup_scheduler()
    
    def _setup_platforms(self):
        """Setup platform integrations"""
        try:
            # Twitter
            if config.social_media.twitter_api_key:
                twitter_creds = PlatformCredentials(
                    platform=Platform.TWITTER,
                    api_key=config.social_media.twitter_api_key,
                    api_secret=config.social_media.twitter_api_secret,
                    access_token=config.social_media.twitter_access_token,
                    access_token_secret=config.social_media.twitter_access_token_secret,
                    bearer_token=config.social_media.twitter_bearer_token
                )
                self.platforms[Platform.TWITTER] = TwitterPlatform(twitter_creds)
            
            # Facebook
            if config.social_media.facebook_access_token:
                facebook_creds = PlatformCredentials(
                    platform=Platform.FACEBOOK,
                    access_token=config.social_media.facebook_access_token,
                    app_id=config.social_media.facebook_app_id,
                    app_secret=config.social_media.facebook_app_secret,
                    page_id=config.social_media.facebook_page_id
                )
                self.platforms[Platform.FACEBOOK] = FacebookPlatform(facebook_creds)
            
            # LinkedIn
            if config.social_media.linkedin_access_token:
                linkedin_creds = PlatformCredentials(
                    platform=Platform.LINKEDIN,
                    access_token=config.social_media.linkedin_access_token,
                    client_id=config.social_media.linkedin_client_id,
                    client_secret=config.social_media.linkedin_client_secret
                )
                self.platforms[Platform.LINKEDIN] = LinkedInPlatform(linkedin_creds)
            
            # Instagram
            if config.social_media.instagram_username:
                instagram_creds = PlatformCredentials(
                    platform=Platform.INSTAGRAM,
                    username=config.social_media.instagram_username,
                    password=config.social_media.instagram_password
                )
                self.platforms[Platform.INSTAGRAM] = InstagramPlatform(instagram_creds)
            
            # Pinterest
            if config.social_media.pinterest_access_token:
                pinterest_creds = PlatformCredentials(
                    platform=Platform.PINTEREST,
                    access_token=config.social_media.pinterest_access_token,
                    board_id=config.social_media.pinterest_board_id
                )
                self.platforms[Platform.PINTEREST] = PinterestPlatform(pinterest_creds)
            
            logger.info(f"Setup {len(self.platforms)} platform(s)")
            
        except Exception as e:
            logger.error(f"Failed to setup platforms: {e}")
    
    def _setup_scheduler(self):
        """Setup the posting scheduler"""
        # Schedule posting every hour during active hours
        schedule.every().hour.do(self._posting_job)
        
        # Schedule content generation every 6 hours
        schedule.every(6).hours.do(self._generate_content_batch)
        
        # Schedule analytics collection every 2 hours
        schedule.every(2).hours.do(self._collect_analytics)
        
        # Schedule health checks every 30 minutes
        schedule.every(30).minutes.do(self._health_check)
    
    async def start(self):
        """Start the AI agent"""
        try:
            logger.info("Starting AI Social Media Agent...")
            self.is_running = True
            self.status.is_running = True
            self.status.uptime = 0
            
            # Initial health check
            await self._health_check()
            
            # Start the scheduler loop
            await self._run_scheduler()
            
        except Exception as e:
            logger.error(f"Failed to start AI agent: {e}")
            self.is_running = False
            self.status.is_running = False
            raise
    
    async def stop(self):
        """Stop the AI agent"""
        logger.info("Stopping AI Social Media Agent...")
        self.is_running = False
        self.status.is_running = False
        
        # Disconnect from all platforms
        for platform in self.platforms.values():
            try:
                await platform.disconnect()
            except Exception as e:
                logger.warning(f"Failed to disconnect from platform: {e}")
    
    async def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.is_running:
            try:
                schedule.run_pending()
                await asyncio.sleep(60)  # Check every minute
                
                # Update uptime
                if self.status.uptime is not None:
                    self.status.uptime += 60
                
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(60)
    
    async def _posting_job(self):
        """Main posting job"""
        try:
            logger.info("Starting posting job...")
            
            # Check if we're within posting hours
            current_hour = datetime.utcnow().hour
            if not (config.scheduling.posting_start_hour <= current_hour <= config.scheduling.posting_end_hour):
                logger.info("Outside posting hours, skipping...")
                return
            
            # Check daily post limit
            today_posts = len([p for p in self.posting_history 
                             if p.posted_time and p.posted_time.date() == datetime.utcnow().date()])
            
            if today_posts >= config.scheduling.max_daily_posts:
                logger.info("Daily post limit reached, skipping...")
                return
            
            # Generate and post content for each platform
            for platform_name, platform in self.platforms.items():
                try:
                    await self._post_to_platform(platform_name, platform)
                except Exception as e:
                    logger.error(f"Failed to post to {platform_name}: {e}")
                    self.status.failed_posts += 1
            
            logger.info("Posting job completed")
            
        except Exception as e:
            logger.error(f"Posting job failed: {e}")
            self.status.last_error = str(e)
    
    async def _post_to_platform(self, platform_name: Platform, platform: Any):
        """Post content to a specific platform"""
        try:
            # Generate content request
            content_request = ContentRequest(
                platform=platform_name,
                include_media=random.choice([True, False]),
                topic=random.choice([
                    "artificial intelligence", "technology", "business", 
                    "innovation", "startup", "digital transformation"
                ])
            )
            
            # Generate content
            content = await self.content_generator.generate_content(content_request)
            
            # Post to platform
            result = await platform.post_with_retry(content)
            
            # Create post record
            post = SocialMediaPost(
                content=content,
                platform=platform_name,
                status=PostStatus.POSTED,
                posted_time=datetime.utcnow(),
                post_id=result.get("post_id"),
                engagement_metrics=result
            )
            
            self.posting_history.append(post)
            self.status.successful_posts += 1
            self.status.last_post_time = datetime.utcnow()
            
            logger.info(f"Successfully posted to {platform_name}")
            
        except Exception as e:
            logger.error(f"Failed to post to {platform_name}: {e}")
            raise
    
    async def _generate_content_batch(self):
        """Generate content in batch for future use"""
        try:
            logger.info("Generating content batch...")
            
            # Generate content for each platform
            requests = []
            for platform_name in self.platforms.keys():
                request = ContentRequest(
                    platform=platform_name,
                    include_media=random.choice([True, False])
                )
                requests.append(request)
            
            # Generate content
            contents = await self.content_generator.generate_content_batch(requests)
            
            logger.info(f"Generated {len(contents)} content pieces")
            
        except Exception as e:
            logger.error(f"Content generation failed: {e}")
    
    async def _collect_analytics(self):
        """Collect analytics from all platforms"""
        try:
            logger.info("Collecting analytics...")
            
            for platform_name, platform in self.platforms.items():
                try:
                    # Get recent posts for this platform
                    recent_posts = [p for p in self.posting_history 
                                  if p.platform == platform_name and p.post_id]
                    
                    for post in recent_posts[-5:]:  # Last 5 posts
                        metrics = await platform.get_engagement_metrics(post.post_id)
                        if metrics and metrics.get("status") != "error":
                            post.engagement_metrics = metrics
                
                except Exception as e:
                    logger.warning(f"Failed to collect analytics for {platform_name}: {e}")
            
            logger.info("Analytics collection completed")
            
        except Exception as e:
            logger.error(f"Analytics collection failed: {e}")
    
    async def _health_check(self):
        """Perform health check on all platforms"""
        try:
            logger.info("Performing health check...")
            
            health_results = []
            for platform_name, platform in self.platforms.items():
                try:
                    health = await platform.health_check()
                    health_results.append(health)
                    
                    if health["status"] == "healthy":
                        logger.info(f"{platform_name}: Healthy")
                    else:
                        logger.warning(f"{platform_name}: {health.get('status', 'Unknown')}")
                
                except Exception as e:
                    logger.error(f"Health check failed for {platform_name}: {e}")
                    health_results.append({
                        "platform": platform_name,
                        "status": "error",
                        "error": str(e)
                    })
            
            # Update agent status
            self.status.active_platforms = [
                Platform(h["platform"]) for h in health_results 
                if h.get("status") == "healthy"
            ]
            
            logger.info(f"Health check completed. {len(self.status.active_platforms)} platforms active")
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
    
    async def get_status(self) -> AgentStatus:
        """Get current agent status"""
        self.status.total_posts_today = len([
            p for p in self.posting_history 
            if p.posted_time and p.posted_time.date() == datetime.utcnow().date()
        ])
        
        self.status.updated_at = datetime.utcnow()
        return self.status
    
    async def get_posting_metrics(self, days: int = 7) -> Dict[str, PostingMetrics]:
        """Get posting metrics for the specified number of days"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        metrics = {}
        
        for platform in Platform:
            platform_posts = [
                p for p in self.posting_history
                if p.platform == platform and p.posted_time
                and start_date <= p.posted_time <= end_date
            ]
            
            if platform_posts:
                total_engagement = sum(
                    p.engagement_metrics.get("likes", 0) + 
                    p.engagement_metrics.get("shares", 0) + 
                    p.engagement_metrics.get("comments", 0)
                    for p in platform_posts if p.engagement_metrics
                )
                
                avg_engagement = total_engagement / len(platform_posts) if platform_posts else 0
                
                metrics[platform.value] = PostingMetrics(
                    date=end_date,
                    platform=platform,
                    posts_scheduled=len([p for p in platform_posts if p.status == PostStatus.SCHEDULED]),
                    posts_posted=len([p for p in platform_posts if p.status == PostStatus.POSTED]),
                    posts_failed=len([p for p in platform_posts if p.status == PostStatus.FAILED]),
                    total_engagement=total_engagement,
                    avg_engagement_rate=avg_engagement
                )
        
        return metrics
    
    async def manual_post(self, platform: Platform, content: str, include_media: bool = False) -> Dict[str, Any]:
        """Manually post content to a specific platform"""
        try:
            if platform not in self.platforms:
                raise ValueError(f"Platform {platform} not configured")
            
            # Create content request
            content_request = ContentRequest(
                platform=platform,
                include_media=include_media,
                custom_prompt=content
            )
            
            # Generate content
            generated_content = await self.content_generator.generate_content(content_request)
            
            # Post to platform
            platform_instance = self.platforms[platform]
            result = await platform_instance.post_with_retry(generated_content)
            
            # Create post record
            post = SocialMediaPost(
                content=generated_content,
                platform=platform,
                status=PostStatus.POSTED,
                posted_time=datetime.utcnow(),
                post_id=result.get("post_id"),
                engagement_metrics=result
            )
            
            self.posting_history.append(post)
            self.status.successful_posts += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Manual post failed: {e}")
            raise
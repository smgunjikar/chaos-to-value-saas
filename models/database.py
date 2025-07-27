from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List, Dict, Any
from config.settings import settings

# Database setup
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    platform = Column(String(50), nullable=False)
    theme = Column(String(100), nullable=True)
    media_urls = Column(JSON, default=list)  # List of media file URLs
    hashtags = Column(JSON, default=list)  # List of hashtags
    scheduled_time = Column(DateTime, nullable=True)
    posted_time = Column(DateTime, nullable=True)
    status = Column(String(20), default="draft")  # draft, scheduled, posted, failed
    platform_post_id = Column(String(100), nullable=True)  # ID from the platform
    engagement_data = Column(JSON, default=dict)  # likes, shares, comments, etc.
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class ContentTemplate(Base):
    __tablename__ = "content_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    template = Column(Text, nullable=False)
    platform = Column(String(50), nullable=False)
    theme = Column(String(100), nullable=False)
    variables = Column(JSON, default=list)  # List of template variables
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Schedule(Base):
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), nullable=False)
    theme = Column(String(100), nullable=False)
    time_pattern = Column(String(100), nullable=False)  # cron-like pattern
    is_active = Column(Boolean, default=True)
    last_execution = Column(DateTime, nullable=True)
    next_execution = Column(DateTime, nullable=True)
    execution_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Analytics(Base):
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, nullable=False)
    platform = Column(String(50), nullable=False)
    metric_name = Column(String(50), nullable=False)  # likes, shares, comments, views
    metric_value = Column(Integer, nullable=False)
    recorded_at = Column(DateTime, default=func.now())

class AIModel(Base):
    __tablename__ = "ai_models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    provider = Column(String(50), nullable=False)  # openai, anthropic
    model_id = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    usage_cost = Column(Float, default=0.0)
    success_rate = Column(Float, default=0.0)
    average_response_time = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class MediaAsset(Base):
    __tablename__ = "media_assets"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # image, video
    file_format = Column(String(20), nullable=False)  # jpg, mp4, etc.
    file_size = Column(Integer, nullable=False)  # bytes
    storage_url = Column(String(500), nullable=False)
    theme = Column(String(100), nullable=True)
    tags = Column(JSON, default=list)
    usage_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

# Database helper functions
def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_db_session() -> Session:
    """Get a database session for direct use"""
    return SessionLocal()

class DatabaseManager:
    """Database operations manager"""
    
    def __init__(self):
        self.session = get_db_session()
    
    def close(self):
        """Close database session"""
        self.session.close()
    
    def create_post(self, content: str, platform: str, theme: str = None, 
                   media_urls: List[str] = None, hashtags: List[str] = None,
                   scheduled_time: datetime = None) -> Post:
        """Create a new post"""
        post = Post(
            content=content,
            platform=platform,
            theme=theme,
            media_urls=media_urls or [],
            hashtags=hashtags or [],
            scheduled_time=scheduled_time
        )
        self.session.add(post)
        self.session.commit()
        self.session.refresh(post)
        return post
    
    def update_post_status(self, post_id: int, status: str, 
                          platform_post_id: str = None, 
                          error_message: str = None) -> bool:
        """Update post status"""
        post = self.session.query(Post).filter(Post.id == post_id).first()
        if post:
            post.status = status
            if platform_post_id:
                post.platform_post_id = platform_post_id
            if error_message:
                post.error_message = error_message
            if status == "posted":
                post.posted_time = func.now()
            self.session.commit()
            return True
        return False
    
    def get_scheduled_posts(self, limit: int = 100) -> List[Post]:
        """Get posts scheduled for posting"""
        return self.session.query(Post).filter(
            Post.status == "scheduled",
            Post.scheduled_time <= func.now()
        ).limit(limit).all()
    
    def record_analytics(self, post_id: int, platform: str, 
                        metrics: Dict[str, int]):
        """Record analytics data"""
        for metric_name, metric_value in metrics.items():
            analytics = Analytics(
                post_id=post_id,
                platform=platform,
                metric_name=metric_name,
                metric_value=metric_value
            )
            self.session.add(analytics)
        self.session.commit()
    
    def get_performance_stats(self, platform: str = None, 
                            days: int = 30) -> Dict[str, Any]:
        """Get performance statistics"""
        query = self.session.query(Post)
        if platform:
            query = query.filter(Post.platform == platform)
        
        # Get posts from last N days
        from datetime import timedelta
        cutoff_date = func.now() - timedelta(days=days)
        posts = query.filter(Post.created_at >= cutoff_date).all()
        
        stats = {
            "total_posts": len(posts),
            "successful_posts": len([p for p in posts if p.status == "posted"]),
            "failed_posts": len([p for p in posts if p.status == "failed"]),
            "platforms": {}
        }
        
        # Platform-specific stats
        for post in posts:
            if post.platform not in stats["platforms"]:
                stats["platforms"][post.platform] = {
                    "total": 0, "successful": 0, "failed": 0
                }
            stats["platforms"][post.platform]["total"] += 1
            if post.status == "posted":
                stats["platforms"][post.platform]["successful"] += 1
            elif post.status == "failed":
                stats["platforms"][post.platform]["failed"] += 1
        
        return stats
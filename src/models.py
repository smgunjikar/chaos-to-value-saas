"""
Data models for the AI Social Media Agent
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class ContentType(str, Enum):
    """Types of content that can be generated"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    CAROUSEL = "carousel"
    STORY = "story"
    REEL = "reel"


class Platform(str, Enum):
    """Supported social media platforms"""
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    PINTEREST = "pinterest"


class PostStatus(str, Enum):
    """Status of a social media post"""
    PENDING = "pending"
    POSTED = "posted"
    FAILED = "failed"
    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"


class ContentRequest(BaseModel):
    """Request for content generation"""
    platform: Platform
    content_type: ContentType = ContentType.TEXT
    include_media: bool = False
    topic: Optional[str] = None
    tone: Optional[str] = None
    target_audience: Optional[str] = None
    max_length: Optional[int] = None
    hashtags: Optional[List[str]] = None
    custom_prompt: Optional[str] = None


class GeneratedContent(BaseModel):
    """Generated content for social media"""
    text: str
    hashtags: List[str] = []
    media_urls: List[str] = []
    platform: Platform
    content_type: ContentType
    generated_at: datetime
    ai_model: str
    topic: Optional[str] = None
    engagement_score: Optional[float] = None
    sentiment_score: Optional[float] = None


class SocialMediaPost(BaseModel):
    """A social media post"""
    id: Optional[str] = None
    content: GeneratedContent
    platform: Platform
    status: PostStatus = PostStatus.PENDING
    scheduled_time: Optional[datetime] = None
    posted_time: Optional[datetime] = None
    post_id: Optional[str] = None  # ID from the platform
    engagement_metrics: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PostingSchedule(BaseModel):
    """Schedule for posting content"""
    id: Optional[str] = None
    platform: Platform
    frequency: str  # "hourly", "daily", "weekly", "custom"
    interval_minutes: int = 60
    start_time: datetime
    end_time: Optional[datetime] = None
    timezone: str = "UTC"
    is_active: bool = True
    content_types: List[ContentType] = [ContentType.TEXT]
    topics: Optional[List[str]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AnalyticsData(BaseModel):
    """Analytics data for posts"""
    post_id: str
    platform: Platform
    likes: int = 0
    shares: int = 0
    comments: int = 0
    views: int = 0
    clicks: int = 0
    engagement_rate: float = 0.0
    reach: int = 0
    impressions: int = 0
    collected_at: datetime = Field(default_factory=datetime.utcnow)


class PlatformCredentials(BaseModel):
    """Credentials for social media platforms"""
    platform: Platform
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    access_token_secret: Optional[str] = None
    bearer_token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    app_id: Optional[str] = None
    app_secret: Optional[str] = None
    page_id: Optional[str] = None
    board_id: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ContentTemplate(BaseModel):
    """Template for content generation"""
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    template: str
    platform: Platform
    content_type: ContentType
    variables: List[str] = []
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TrendingTopic(BaseModel):
    """Trending topic data"""
    topic: str
    platform: Platform
    trend_score: float
    hashtag: Optional[str] = None
    volume: Optional[int] = None
    collected_at: datetime = Field(default_factory=datetime.utcnow)


class AgentStatus(BaseModel):
    """Status of the AI agent"""
    is_running: bool = False
    last_post_time: Optional[datetime] = None
    total_posts_today: int = 0
    successful_posts: int = 0
    failed_posts: int = 0
    active_platforms: List[Platform] = []
    current_tasks: List[str] = []
    uptime: Optional[float] = None
    last_error: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PostingMetrics(BaseModel):
    """Metrics for posting performance"""
    date: datetime
    platform: Platform
    posts_scheduled: int = 0
    posts_posted: int = 0
    posts_failed: int = 0
    total_engagement: int = 0
    avg_engagement_rate: float = 0.0
    best_performing_post: Optional[str] = None
    worst_performing_post: Optional[str] = None


class ContentCategory(BaseModel):
    """Content categories for organization"""
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    keywords: List[str] = []
    platforms: List[Platform] = []
    content_types: List[ContentType] = []
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
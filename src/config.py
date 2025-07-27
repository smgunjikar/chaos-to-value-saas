"""
Configuration settings for the AI Social Media Agent
"""

import os
from typing import Dict, List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class SocialMediaConfig(BaseSettings):
    """Configuration for social media platforms"""
    
    # Twitter/X Configuration
    twitter_api_key: Optional[str] = Field(default=None, env="TWITTER_API_KEY")
    twitter_api_secret: Optional[str] = Field(default=None, env="TWITTER_API_SECRET")
    twitter_access_token: Optional[str] = Field(default=None, env="TWITTER_ACCESS_TOKEN")
    twitter_access_token_secret: Optional[str] = Field(default=None, env="TWITTER_ACCESS_TOKEN_SECRET")
    twitter_bearer_token: Optional[str] = Field(default=None, env="TWITTER_BEARER_TOKEN")
    
    # Facebook Configuration
    facebook_app_id: Optional[str] = Field(default=None, env="FACEBOOK_APP_ID")
    facebook_app_secret: Optional[str] = Field(default=None, env="FACEBOOK_APP_SECRET")
    facebook_access_token: Optional[str] = Field(default=None, env="FACEBOOK_ACCESS_TOKEN")
    facebook_page_id: Optional[str] = Field(default=None, env="FACEBOOK_PAGE_ID")
    
    # LinkedIn Configuration
    linkedin_client_id: Optional[str] = Field(default=None, env="LINKEDIN_CLIENT_ID")
    linkedin_client_secret: Optional[str] = Field(default=None, env="LINKEDIN_CLIENT_SECRET")
    linkedin_access_token: Optional[str] = Field(default=None, env="LINKEDIN_ACCESS_TOKEN")
    
    # Instagram Configuration
    instagram_username: Optional[str] = Field(default=None, env="INSTAGRAM_USERNAME")
    instagram_password: Optional[str] = Field(default=None, env="INSTAGRAM_PASSWORD")
    
    # Pinterest Configuration
    pinterest_access_token: Optional[str] = Field(default=None, env="PINTEREST_ACCESS_TOKEN")
    pinterest_board_id: Optional[str] = Field(default=None, env="PINTEREST_BOARD_ID")


class AIConfig(BaseSettings):
    """Configuration for AI services"""
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4", env="OPENAI_MODEL")
    openai_max_tokens: int = Field(default=1000, env="OPENAI_MAX_TOKENS")
    
    # Anthropic Configuration
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-3-sonnet-20240229", env="ANTHROPIC_MODEL")
    
    # Content Generation Settings
    content_templates: List[str] = Field(default=[
        "Create an engaging post about {topic}",
        "Share an interesting fact about {topic}",
        "What's your take on {topic}?",
        "Here's something fascinating about {topic}",
        "Let's discuss {topic} today!"
    ])
    
    hashtag_strategy: str = Field(default="trending", env="HASHTAG_STRATEGY")
    max_hashtags: int = Field(default=5, env="MAX_HASHTAGS")


class DatabaseConfig(BaseSettings):
    """Database configuration"""
    
    database_url: str = Field(default="sqlite:///./social_media_agent.db", env="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")


class SchedulingConfig(BaseSettings):
    """Scheduling configuration"""
    
    # Posting intervals (in minutes)
    min_interval: int = Field(default=60, env="MIN_POSTING_INTERVAL")
    max_interval: int = Field(default=240, env="MAX_POSTING_INTERVAL")
    
    # Time zones and posting windows
    timezone: str = Field(default="UTC", env="TIMEZONE")
    posting_start_hour: int = Field(default=8, env="POSTING_START_HOUR")
    posting_end_hour: int = Field(default=22, env="POSTING_END_HOUR")
    
    # Content variety settings
    content_rotation_days: int = Field(default=7, env="CONTENT_ROTATION_DAYS")
    max_daily_posts: int = Field(default=10, env="MAX_DAILY_POSTS")


class MonitoringConfig(BaseSettings):
    """Monitoring and logging configuration"""
    
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=8000, env="METRICS_PORT")
    
    # Alert settings
    enable_alerts: bool = Field(default=True, env="ENABLE_ALERTS")
    alert_webhook_url: Optional[str] = Field(default=None, env="ALERT_WEBHOOK_URL")


class Config(BaseSettings):
    """Main configuration class"""
    
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Sub-configurations
    social_media: SocialMediaConfig = SocialMediaConfig()
    ai: AIConfig = AIConfig()
    database: DatabaseConfig = DatabaseConfig()
    scheduling: SchedulingConfig = SchedulingConfig()
    monitoring: MonitoringConfig = MonitoringConfig()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global configuration instance
config = Config()
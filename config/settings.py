import os
from typing import List, Dict, Any
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # AI Service Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    anthropic_api_key: str = Field(..., env="ANTHROPIC_API_KEY")
    
    # Twitter/X Configuration
    twitter_api_key: str = Field(..., env="TWITTER_API_KEY")
    twitter_api_secret: str = Field(..., env="TWITTER_API_SECRET")
    twitter_access_token: str = Field(..., env="TWITTER_ACCESS_TOKEN")
    twitter_access_token_secret: str = Field(..., env="TWITTER_ACCESS_TOKEN_SECRET")
    twitter_bearer_token: str = Field(..., env="TWITTER_BEARER_TOKEN")
    
    # Facebook Configuration
    facebook_access_token: str = Field(..., env="FACEBOOK_ACCESS_TOKEN")
    facebook_page_id: str = Field(..., env="FACEBOOK_PAGE_ID")
    
    # Instagram Configuration
    instagram_username: str = Field(..., env="INSTAGRAM_USERNAME")
    instagram_password: str = Field(..., env="INSTAGRAM_PASSWORD")
    
    # LinkedIn Configuration
    linkedin_client_id: str = Field(..., env="LINKEDIN_CLIENT_ID")
    linkedin_client_secret: str = Field(..., env="LINKEDIN_CLIENT_SECRET")
    linkedin_access_token: str = Field(..., env="LINKEDIN_ACCESS_TOKEN")
    
    # TikTok Configuration
    tiktok_session_id: str = Field(..., env="TIKTOK_SESSION_ID")
    
    # Database Configuration
    database_url: str = Field(..., env="DATABASE_URL")
    redis_url: str = Field(..., env="REDIS_URL")
    
    # Content Generation Settings
    content_themes: List[str] = Field(
        default_factory=lambda: ["technology", "business", "motivation", "lifestyle"],
        env="CONTENT_THEMES"
    )
    post_frequency_hours: int = Field(default=4, env="POST_FREQUENCY_HOURS")
    max_posts_per_day: int = Field(default=6, env="MAX_POSTS_PER_DAY")
    content_variation: str = Field(default="high", env="CONTENT_VARIATION")
    
    # AWS S3 Configuration
    aws_access_key_id: str = Field(default="", env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(default="", env="AWS_SECRET_ACCESS_KEY")
    aws_s3_bucket: str = Field(default="", env="AWS_S3_BUCKET")
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")
    
    # Application Settings
    app_env: str = Field(default="development", env="APP_ENV")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    timezone: str = Field(default="UTC", env="TIMEZONE")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if isinstance(self.content_themes, str):
            self.content_themes = [theme.strip() for theme in self.content_themes.split(",")]

# Global settings instance
settings = Settings()

# Platform configurations
PLATFORM_CONFIGS = {
    "twitter": {
        "max_text_length": 280,
        "supports_images": True,
        "supports_videos": True,
        "max_images": 4,
        "video_formats": ["mp4", "mov"],
        "image_formats": ["jpg", "jpeg", "png", "gif"]
    },
    "instagram": {
        "max_text_length": 2200,
        "supports_images": True,
        "supports_videos": True,
        "max_images": 10,
        "video_formats": ["mp4", "mov"],
        "image_formats": ["jpg", "jpeg", "png"]
    },
    "facebook": {
        "max_text_length": 63206,
        "supports_images": True,
        "supports_videos": True,
        "max_images": 20,
        "video_formats": ["mp4", "mov", "avi"],
        "image_formats": ["jpg", "jpeg", "png", "gif"]
    },
    "linkedin": {
        "max_text_length": 3000,
        "supports_images": True,
        "supports_videos": True,
        "max_images": 9,
        "video_formats": ["mp4", "mov"],
        "image_formats": ["jpg", "jpeg", "png"]
    },
    "tiktok": {
        "max_text_length": 150,
        "supports_images": False,
        "supports_videos": True,
        "max_images": 0,
        "video_formats": ["mp4"],
        "image_formats": []
    }
}
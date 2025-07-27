"""
Base platform class for social media integrations
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from loguru import logger

from ..models import Platform, SocialMediaPost, GeneratedContent, PostStatus, PlatformCredentials


class BasePlatform(ABC):
    """Base class for social media platform integrations"""
    
    def __init__(self, credentials: PlatformCredentials):
        self.credentials = credentials
        self.platform = credentials.platform
        self.is_connected = False
        self.client = None
        self._setup_client()
    
    @abstractmethod
    def _setup_client(self):
        """Setup the platform client"""
        pass
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the platform"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Disconnect from the platform"""
        pass
    
    @abstractmethod
    async def post_content(self, content: GeneratedContent) -> Dict[str, Any]:
        """Post content to the platform"""
        pass
    
    @abstractmethod
    async def get_post_status(self, post_id: str) -> Dict[str, Any]:
        """Get the status of a posted content"""
        pass
    
    @abstractmethod
    async def get_engagement_metrics(self, post_id: str) -> Dict[str, Any]:
        """Get engagement metrics for a post"""
        pass
    
    @abstractmethod
    async def delete_post(self, post_id: str) -> bool:
        """Delete a post from the platform"""
        pass
    
    @abstractmethod
    async def get_trending_topics(self) -> List[str]:
        """Get trending topics from the platform"""
        pass
    
    async def validate_credentials(self) -> bool:
        """Validate platform credentials"""
        try:
            return await self.connect()
        except Exception as e:
            logger.error(f"Failed to validate credentials for {self.platform}: {e}")
            return False
        finally:
            await self.disconnect()
    
    async def post_with_retry(self, content: GeneratedContent, max_retries: int = 3) -> Dict[str, Any]:
        """Post content with retry logic"""
        for attempt in range(max_retries):
            try:
                if not self.is_connected:
                    await self.connect()
                
                result = await self.post_content(content)
                logger.info(f"Successfully posted to {self.platform} on attempt {attempt + 1}")
                return result
                
            except Exception as e:
                logger.warning(f"Post attempt {attempt + 1} failed for {self.platform}: {e}")
                
                if attempt == max_retries - 1:
                    logger.error(f"All retry attempts failed for {self.platform}")
                    raise
                
                # Wait before retry
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    def format_content_for_platform(self, content: GeneratedContent) -> str:
        """Format content specifically for this platform"""
        formatted_text = content.text
        
        # Add hashtags
        if content.hashtags:
            hashtags_text = " ".join(content.hashtags)
            formatted_text += f"\n\n{hashtags_text}"
        
        return formatted_text
    
    def get_platform_limits(self) -> Dict[str, Any]:
        """Get platform-specific limits"""
        limits = {
            Platform.TWITTER: {
                "max_text_length": 280,
                "max_hashtags": 30,
                "max_media": 4
            },
            Platform.FACEBOOK: {
                "max_text_length": 63206,
                "max_hashtags": 30,
                "max_media": 10
            },
            Platform.LINKEDIN: {
                "max_text_length": 3000,
                "max_hashtags": 30,
                "max_media": 9
            },
            Platform.INSTAGRAM: {
                "max_text_length": 2200,
                "max_hashtags": 30,
                "max_media": 10
            },
            Platform.PINTEREST: {
                "max_text_length": 500,
                "max_hashtags": 20,
                "max_media": 1
            }
        }
        
        return limits.get(self.platform, {})
    
    def validate_content(self, content: GeneratedContent) -> bool:
        """Validate content against platform limits"""
        limits = self.get_platform_limits()
        
        if not limits:
            return True
        
        # Check text length
        max_length = limits.get("max_text_length")
        if max_length and len(content.text) > max_length:
            logger.warning(f"Content text exceeds {self.platform} limit of {max_length}")
            return False
        
        # Check hashtag count
        max_hashtags = limits.get("max_hashtags")
        if max_hashtags and len(content.hashtags) > max_hashtags:
            logger.warning(f"Hashtag count exceeds {self.platform} limit of {max_hashtags}")
            return False
        
        # Check media count
        max_media = limits.get("max_media")
        if max_media and len(content.media_urls) > max_media:
            logger.warning(f"Media count exceeds {self.platform} limit of {max_media}")
            return False
        
        return True
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the platform"""
        try:
            is_connected = await self.connect()
            return {
                "platform": self.platform,
                "is_connected": is_connected,
                "credentials_valid": self.credentials.is_active,
                "status": "healthy" if is_connected else "unhealthy"
            }
        except Exception as e:
            return {
                "platform": self.platform,
                "is_connected": False,
                "credentials_valid": self.credentials.is_active,
                "status": "error",
                "error": str(e)
            }
        finally:
            await self.disconnect()


import asyncio
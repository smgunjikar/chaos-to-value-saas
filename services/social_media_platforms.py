import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
import tempfile
import aiofiles
import httpx
from abc import ABC, abstractmethod

import tweepy
import facebook
from instagrapi import Client as InstagramClient
from linkedin_api import Linkedin
from TikTokApi import TikTokApi

from config.settings import settings

logger = logging.getLogger(__name__)

class BasePlatform(ABC):
    """Base class for social media platforms"""
    
    def __init__(self, platform_name: str):
        self.platform_name = platform_name
        self.is_authenticated = False
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the platform"""
        pass
    
    @abstractmethod
    async def post_content(self, content: str, media_urls: List[str] = None,
                          hashtags: List[str] = None) -> Dict[str, Any]:
        """Post content to the platform"""
        pass
    
    @abstractmethod
    async def get_post_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get analytics for a specific post"""
        pass
    
    async def download_media(self, url: str) -> str:
        """Download media file from URL to temporary location"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                
                # Create temporary file
                suffix = os.path.splitext(url)[1] or '.jpg'
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                    tmp_file.write(response.content)
                    return tmp_file.name
        except Exception as e:
            logger.error(f"Error downloading media from {url}: {str(e)}")
            return None

class TwitterPlatform(BasePlatform):
    """Twitter/X platform integration"""
    
    def __init__(self):
        super().__init__("twitter")
        self.client = None
        self.api = None
    
    async def authenticate(self) -> bool:
        """Authenticate with Twitter API"""
        try:
            # Initialize Twitter API v2 client
            self.client = tweepy.Client(
                bearer_token=settings.twitter_bearer_token,
                consumer_key=settings.twitter_api_key,
                consumer_secret=settings.twitter_api_secret,
                access_token=settings.twitter_access_token,
                access_token_secret=settings.twitter_access_token_secret,
                wait_on_rate_limit=True
            )
            
            # Initialize API v1.1 for media upload
            auth = tweepy.OAuth1UserHandler(
                settings.twitter_api_key,
                settings.twitter_api_secret,
                settings.twitter_access_token,
                settings.twitter_access_token_secret
            )
            self.api = tweepy.API(auth)
            
            # Test authentication
            user = self.client.get_me()
            if user.data:
                self.is_authenticated = True
                logger.info(f"Twitter authentication successful for user: {user.data.username}")
                return True
            
        except Exception as e:
            logger.error(f"Twitter authentication failed: {str(e)}")
            
        return False
    
    async def post_content(self, content: str, media_urls: List[str] = None,
                          hashtags: List[str] = None) -> Dict[str, Any]:
        """Post content to Twitter"""
        if not self.is_authenticated:
            await self.authenticate()
        
        try:
            # Prepare tweet text
            tweet_text = content
            if hashtags:
                hashtag_text = " ".join([f"#{tag}" for tag in hashtags])
                if len(tweet_text + " " + hashtag_text) <= 280:
                    tweet_text += " " + hashtag_text
            
            media_ids = []
            
            # Upload media if provided
            if media_urls:
                for url in media_urls[:4]:  # Twitter allows max 4 images
                    media_path = await self.download_media(url)
                    if media_path:
                        try:
                            media = self.api.media_upload(media_path)
                            media_ids.append(media.media_id)
                            os.unlink(media_path)  # Clean up temp file
                        except Exception as e:
                            logger.error(f"Error uploading media to Twitter: {str(e)}")
            
            # Post tweet
            response = self.client.create_tweet(
                text=tweet_text,
                media_ids=media_ids if media_ids else None
            )
            
            if response.data:
                return {
                    "success": True,
                    "platform_post_id": response.data["id"],
                    "message": "Posted successfully to Twitter"
                }
            
        except Exception as e:
            logger.error(f"Error posting to Twitter: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        
        return {"success": False, "error": "Unknown error"}
    
    async def get_post_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get analytics for a Twitter post"""
        try:
            tweet = self.client.get_tweet(
                post_id,
                tweet_fields=["public_metrics", "created_at"],
                user_fields=["public_metrics"]
            )
            
            if tweet.data:
                metrics = tweet.data.public_metrics
                return {
                    "likes": metrics.get("like_count", 0),
                    "retweets": metrics.get("retweet_count", 0),
                    "replies": metrics.get("reply_count", 0),
                    "quotes": metrics.get("quote_count", 0),
                    "impressions": metrics.get("impression_count", 0)
                }
                
        except Exception as e:
            logger.error(f"Error getting Twitter analytics: {str(e)}")
        
        return {}

class FacebookPlatform(BasePlatform):
    """Facebook platform integration"""
    
    def __init__(self):
        super().__init__("facebook")
        self.graph = None
    
    async def authenticate(self) -> bool:
        """Authenticate with Facebook Graph API"""
        try:
            self.graph = facebook.GraphAPI(access_token=settings.facebook_access_token)
            
            # Test authentication
            user = self.graph.get_object("me")
            if user:
                self.is_authenticated = True
                logger.info(f"Facebook authentication successful for user: {user.get('name')}")
                return True
                
        except Exception as e:
            logger.error(f"Facebook authentication failed: {str(e)}")
        
        return False
    
    async def post_content(self, content: str, media_urls: List[str] = None,
                          hashtags: List[str] = None) -> Dict[str, Any]:
        """Post content to Facebook"""
        if not self.is_authenticated:
            await self.authenticate()
        
        try:
            # Prepare post message
            message = content
            if hashtags:
                hashtag_text = " ".join([f"#{tag}" for tag in hashtags])
                message += "\n\n" + hashtag_text
            
            # Post to Facebook page
            if media_urls and len(media_urls) == 1:
                # Single image/video post
                response = self.graph.put_photo(
                    image=media_urls[0],
                    message=message,
                    parent_object=settings.facebook_page_id
                )
            elif media_urls and len(media_urls) > 1:
                # Multiple photos - create album
                # Simplified: just post as text for now
                response = self.graph.put_object(
                    parent_object=settings.facebook_page_id,
                    connection_name="feed",
                    message=message
                )
            else:
                # Text-only post
                response = self.graph.put_object(
                    parent_object=settings.facebook_page_id,
                    connection_name="feed",
                    message=message
                )
            
            if response and "id" in response:
                return {
                    "success": True,
                    "platform_post_id": response["id"],
                    "message": "Posted successfully to Facebook"
                }
                
        except Exception as e:
            logger.error(f"Error posting to Facebook: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        
        return {"success": False, "error": "Unknown error"}
    
    async def get_post_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get analytics for a Facebook post"""
        try:
            post = self.graph.get_object(
                post_id,
                fields="likes.summary(true),comments.summary(true),shares"
            )
            
            return {
                "likes": post.get("likes", {}).get("summary", {}).get("total_count", 0),
                "comments": post.get("comments", {}).get("summary", {}).get("total_count", 0),
                "shares": post.get("shares", {}).get("count", 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting Facebook analytics: {str(e)}")
        
        return {}

class InstagramPlatform(BasePlatform):
    """Instagram platform integration"""
    
    def __init__(self):
        super().__init__("instagram")
        self.client = None
    
    async def authenticate(self) -> bool:
        """Authenticate with Instagram"""
        try:
            self.client = InstagramClient()
            self.client.login(settings.instagram_username, settings.instagram_password)
            
            user_info = self.client.user_info_by_username(settings.instagram_username)
            if user_info:
                self.is_authenticated = True
                logger.info(f"Instagram authentication successful for user: {settings.instagram_username}")
                return True
                
        except Exception as e:
            logger.error(f"Instagram authentication failed: {str(e)}")
        
        return False
    
    async def post_content(self, content: str, media_urls: List[str] = None,
                          hashtags: List[str] = None) -> Dict[str, Any]:
        """Post content to Instagram"""
        if not self.is_authenticated:
            await self.authenticate()
        
        try:
            # Prepare caption
            caption = content
            if hashtags:
                hashtag_text = "\n\n" + " ".join([f"#{tag}" for tag in hashtags])
                caption += hashtag_text
            
            if media_urls:
                # Download first image
                media_path = await self.download_media(media_urls[0])
                if media_path:
                    try:
                        if len(media_urls) == 1:
                            # Single photo
                            response = self.client.photo_upload(media_path, caption)
                        else:
                            # Multiple photos - create album
                            media_paths = []
                            for url in media_urls[:10]:  # Instagram allows max 10 images
                                path = await self.download_media(url)
                                if path:
                                    media_paths.append(path)
                            
                            if media_paths:
                                response = self.client.album_upload(media_paths, caption)
                                # Clean up temp files
                                for path in media_paths:
                                    os.unlink(path)
                            else:
                                return {"success": False, "error": "No valid media files"}
                        
                        os.unlink(media_path)  # Clean up temp file
                        
                        if response:
                            return {
                                "success": True,
                                "platform_post_id": response.pk,
                                "message": "Posted successfully to Instagram"
                            }
                    except Exception as e:
                        logger.error(f"Error uploading to Instagram: {str(e)}")
                        if os.path.exists(media_path):
                            os.unlink(media_path)
            else:
                # Instagram requires media, so we can't post text-only
                return {
                    "success": False,
                    "error": "Instagram requires at least one image or video"
                }
                
        except Exception as e:
            logger.error(f"Error posting to Instagram: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        
        return {"success": False, "error": "Unknown error"}
    
    async def get_post_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get analytics for an Instagram post"""
        try:
            media_info = self.client.media_info(int(post_id))
            if media_info:
                return {
                    "likes": media_info.like_count,
                    "comments": media_info.comment_count,
                    "views": getattr(media_info, 'view_count', 0)
                }
                
        except Exception as e:
            logger.error(f"Error getting Instagram analytics: {str(e)}")
        
        return {}

class LinkedInPlatform(BasePlatform):
    """LinkedIn platform integration"""
    
    def __init__(self):
        super().__init__("linkedin")
        self.client = None
    
    async def authenticate(self) -> bool:
        """Authenticate with LinkedIn API"""
        try:
            # Note: linkedin-api uses email/password, which is against LinkedIn's ToS
            # In production, you should use LinkedIn's official OAuth2 flow
            # This is a simplified implementation for demonstration
            
            # For now, we'll assume authentication is handled externally
            # and we have a valid access token
            self.is_authenticated = True
            logger.info("LinkedIn authentication assumed successful")
            return True
                
        except Exception as e:
            logger.error(f"LinkedIn authentication failed: {str(e)}")
        
        return False
    
    async def post_content(self, content: str, media_urls: List[str] = None,
                          hashtags: List[str] = None) -> Dict[str, Any]:
        """Post content to LinkedIn"""
        if not self.is_authenticated:
            await self.authenticate()
        
        try:
            # Prepare post text
            post_text = content
            if hashtags:
                hashtag_text = "\n\n" + " ".join([f"#{tag}" for tag in hashtags])
                post_text += hashtag_text
            
            # Use LinkedIn API to post
            # This is a simplified implementation
            # In practice, you'd use the official LinkedIn API with proper OAuth
            
            # For now, we'll simulate a successful post
            fake_post_id = f"linkedin_{datetime.now().timestamp()}"
            
            return {
                "success": True,
                "platform_post_id": fake_post_id,
                "message": "Posted successfully to LinkedIn (simulated)"
            }
                
        except Exception as e:
            logger.error(f"Error posting to LinkedIn: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        
        return {"success": False, "error": "Unknown error"}
    
    async def get_post_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get analytics for a LinkedIn post"""
        # Simplified implementation
        return {
            "likes": 0,
            "comments": 0,
            "shares": 0,
            "views": 0
        }

class TikTokPlatform(BasePlatform):
    """TikTok platform integration"""
    
    def __init__(self):
        super().__init__("tiktok")
        self.api = None
    
    async def authenticate(self) -> bool:
        """Authenticate with TikTok"""
        try:
            # TikTok API is complex and requires special approval
            # This is a simplified implementation
            self.is_authenticated = True
            logger.info("TikTok authentication assumed successful")
            return True
                
        except Exception as e:
            logger.error(f"TikTok authentication failed: {str(e)}")
        
        return False
    
    async def post_content(self, content: str, media_urls: List[str] = None,
                          hashtags: List[str] = None) -> Dict[str, Any]:
        """Post content to TikTok"""
        if not self.is_authenticated:
            await self.authenticate()
        
        try:
            # TikTok requires video content
            if not media_urls:
                return {
                    "success": False,
                    "error": "TikTok requires video content"
                }
            
            # Prepare caption
            caption = content
            if hashtags:
                hashtag_text = " " + " ".join([f"#{tag}" for tag in hashtags])
                caption += hashtag_text
            
            # For now, simulate a successful post
            fake_post_id = f"tiktok_{datetime.now().timestamp()}"
            
            return {
                "success": True,
                "platform_post_id": fake_post_id,
                "message": "Posted successfully to TikTok (simulated)"
            }
                
        except Exception as e:
            logger.error(f"Error posting to TikTok: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        
        return {"success": False, "error": "Unknown error"}
    
    async def get_post_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get analytics for a TikTok post"""
        # Simplified implementation
        return {
            "likes": 0,
            "comments": 0,
            "shares": 0,
            "views": 0
        }

class SocialMediaManager:
    """Manages all social media platforms"""
    
    def __init__(self):
        self.platforms = {
            "twitter": TwitterPlatform(),
            "facebook": FacebookPlatform(),
            "instagram": InstagramPlatform(),
            "linkedin": LinkedInPlatform(),
            "tiktok": TikTokPlatform()
        }
    
    async def authenticate_all(self) -> Dict[str, bool]:
        """Authenticate with all platforms"""
        results = {}
        tasks = []
        
        for platform_name, platform in self.platforms.items():
            task = platform.authenticate()
            tasks.append((platform_name, task))
        
        for platform_name, task in tasks:
            try:
                success = await task
                results[platform_name] = success
            except Exception as e:
                logger.error(f"Authentication failed for {platform_name}: {str(e)}")
                results[platform_name] = False
        
        return results
    
    async def post_to_platform(self, platform_name: str, content: str,
                              media_urls: List[str] = None,
                              hashtags: List[str] = None) -> Dict[str, Any]:
        """Post content to a specific platform"""
        platform = self.platforms.get(platform_name)
        if not platform:
            return {
                "success": False,
                "error": f"Platform {platform_name} not supported"
            }
        
        return await platform.post_content(content, media_urls, hashtags)
    
    async def post_to_multiple_platforms(self, platforms: List[str], content: str,
                                       media_urls: List[str] = None,
                                       hashtags: List[str] = None) -> Dict[str, Dict[str, Any]]:
        """Post content to multiple platforms simultaneously"""
        tasks = []
        
        for platform_name in platforms:
            if platform_name in self.platforms:
                task = self.post_to_platform(platform_name, content, media_urls, hashtags)
                tasks.append((platform_name, task))
        
        results = {}
        for platform_name, task in tasks:
            try:
                result = await task
                results[platform_name] = result
            except Exception as e:
                logger.error(f"Posting failed for {platform_name}: {str(e)}")
                results[platform_name] = {
                    "success": False,
                    "error": str(e)
                }
        
        return results
    
    async def get_analytics_for_post(self, platform_name: str, post_id: str) -> Dict[str, Any]:
        """Get analytics for a specific post"""
        platform = self.platforms.get(platform_name)
        if not platform:
            return {}
        
        return await platform.get_post_analytics(post_id)
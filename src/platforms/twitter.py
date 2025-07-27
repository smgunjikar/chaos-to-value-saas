"""
Twitter/X platform integration
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger

from .base import BasePlatform
from ..models import Platform, GeneratedContent, PlatformCredentials


class TwitterPlatform(BasePlatform):
    """Twitter/X platform integration"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self.api = None
        self.client = None
    
    def _setup_client(self):
        """Setup Twitter API client"""
        try:
            import tweepy
            
            if self.credentials.bearer_token:
                # Use v2 API with bearer token
                self.client = tweepy.Client(
                    bearer_token=self.credentials.bearer_token,
                    consumer_key=self.credentials.api_key,
                    consumer_secret=self.credentials.api_secret,
                    access_token=self.credentials.access_token,
                    access_token_secret=self.credentials.access_token_secret,
                    wait_on_rate_limit=True
                )
            elif self.credentials.api_key and self.credentials.api_secret:
                # Use v1.1 API
                auth = tweepy.OAuthHandler(
                    self.credentials.api_key,
                    self.credentials.api_secret
                )
                auth.set_access_token(
                    self.credentials.access_token,
                    self.credentials.access_token_secret
                )
                self.api = tweepy.API(auth, wait_on_rate_limit=True)
            
            logger.info("Twitter client setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup Twitter client: {e}")
            raise
    
    async def connect(self) -> bool:
        """Connect to Twitter"""
        try:
            if self.client:
                # Test connection with v2 API
                me = self.client.get_me()
                self.is_connected = True
                logger.info(f"Connected to Twitter as @{me.data.username}")
            elif self.api:
                # Test connection with v1.1 API
                me = self.api.verify_credentials()
                self.is_connected = True
                logger.info(f"Connected to Twitter as @{me.screen_name}")
            else:
                self.is_connected = False
                logger.error("No Twitter client available")
            
            return self.is_connected
            
        except Exception as e:
            logger.error(f"Failed to connect to Twitter: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from Twitter"""
        self.is_connected = False
        logger.info("Disconnected from Twitter")
    
    async def post_content(self, content: GeneratedContent) -> Dict[str, Any]:
        """Post content to Twitter"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # Validate content
            if not self.validate_content(content):
                raise ValueError("Content validation failed")
            
            # Format content for Twitter
            formatted_text = self.format_content_for_platform(content)
            
            # Post content
            if self.client:
                # Use v2 API
                response = self.client.create_tweet(text=formatted_text)
                post_id = response.data['id']
                logger.info(f"Posted to Twitter with ID: {post_id}")
                
                return {
                    "post_id": str(post_id),
                    "platform": Platform.TWITTER,
                    "status": "posted",
                    "posted_at": datetime.utcnow(),
                    "url": f"https://twitter.com/user/status/{post_id}"
                }
            
            elif self.api:
                # Use v1.1 API
                status = self.api.update_status(formatted_text)
                logger.info(f"Posted to Twitter with ID: {status.id}")
                
                return {
                    "post_id": str(status.id),
                    "platform": Platform.TWITTER,
                    "status": "posted",
                    "posted_at": datetime.utcnow(),
                    "url": f"https://twitter.com/user/status/{status.id}"
                }
            
            else:
                raise Exception("No Twitter client available")
                
        except Exception as e:
            logger.error(f"Failed to post to Twitter: {e}")
            raise
    
    async def get_post_status(self, post_id: str) -> Dict[str, Any]:
        """Get the status of a Twitter post"""
        try:
            if not self.is_connected:
                await self.connect()
            
            if self.client:
                # Use v2 API
                tweet = self.client.get_tweet(post_id)
                if tweet.data:
                    return {
                        "post_id": post_id,
                        "platform": Platform.TWITTER,
                        "status": "posted",
                        "text": tweet.data.text,
                        "created_at": tweet.data.created_at
                    }
            
            elif self.api:
                # Use v1.1 API
                tweet = self.api.get_status(post_id)
                return {
                    "post_id": post_id,
                    "platform": Platform.TWITTER,
                    "status": "posted",
                    "text": tweet.text,
                    "created_at": tweet.created_at
                }
            
            return {"post_id": post_id, "status": "not_found"}
            
        except Exception as e:
            logger.error(f"Failed to get Twitter post status: {e}")
            return {"post_id": post_id, "status": "error", "error": str(e)}
    
    async def get_engagement_metrics(self, post_id: str) -> Dict[str, Any]:
        """Get engagement metrics for a Twitter post"""
        try:
            if not self.is_connected:
                await self.connect()
            
            if self.client:
                # Use v2 API
                tweet = self.client.get_tweet(
                    post_id,
                    tweet_fields=['public_metrics', 'created_at']
                )
                
                if tweet.data:
                    metrics = tweet.data.public_metrics
                    return {
                        "post_id": post_id,
                        "platform": Platform.TWITTER,
                        "likes": metrics.get('like_count', 0),
                        "retweets": metrics.get('retweet_count', 0),
                        "replies": metrics.get('reply_count', 0),
                        "quotes": metrics.get('quote_count', 0),
                        "impressions": metrics.get('impression_count', 0),
                        "engagement_rate": 0.0  # Calculate based on followers
                    }
            
            elif self.api:
                # Use v1.1 API
                tweet = self.api.get_status(post_id)
                return {
                    "post_id": post_id,
                    "platform": Platform.TWITTER,
                    "likes": tweet.favorite_count,
                    "retweets": tweet.retweet_count,
                    "replies": 0,  # Not available in v1.1
                    "quotes": 0,    # Not available in v1.1
                    "impressions": 0,  # Not available in v1.1
                    "engagement_rate": 0.0
                }
            
            return {"post_id": post_id, "status": "not_found"}
            
        except Exception as e:
            logger.error(f"Failed to get Twitter engagement metrics: {e}")
            return {"post_id": post_id, "status": "error", "error": str(e)}
    
    async def delete_post(self, post_id: str) -> bool:
        """Delete a Twitter post"""
        try:
            if not self.is_connected:
                await self.connect()
            
            if self.client:
                # Use v2 API
                self.client.delete_tweet(post_id)
                logger.info(f"Deleted Twitter post: {post_id}")
                return True
            
            elif self.api:
                # Use v1.1 API
                self.api.destroy_status(post_id)
                logger.info(f"Deleted Twitter post: {post_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete Twitter post: {e}")
            return False
    
    async def get_trending_topics(self) -> List[str]:
        """Get trending topics from Twitter"""
        try:
            if not self.is_connected:
                await self.connect()
            
            trending_topics = []
            
            if self.api:
                # Get trending topics (v1.1 API)
                trends = self.api.get_place_trends(1)  # Worldwide trends
                for trend in trends[0]['trends'][:10]:
                    trending_topics.append(trend['name'])
            
            return trending_topics
            
        except Exception as e:
            logger.error(f"Failed to get Twitter trending topics: {e}")
            return []
    
    def format_content_for_platform(self, content: GeneratedContent) -> str:
        """Format content specifically for Twitter"""
        formatted_text = content.text
        
        # Add hashtags
        if content.hashtags:
            hashtags_text = " ".join(content.hashtags)
            formatted_text += f"\n\n{hashtags_text}"
        
        # Ensure it fits within Twitter's character limit
        max_length = 280
        if len(formatted_text) > max_length:
            # Truncate and add ellipsis
            formatted_text = formatted_text[:max_length-3] + "..."
        
        return formatted_text
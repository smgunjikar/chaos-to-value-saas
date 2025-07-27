"""
Facebook platform integration
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger

from .base import BasePlatform
from ..models import Platform, GeneratedContent, PlatformCredentials


class FacebookPlatform(BasePlatform):
    """Facebook platform integration"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self.graph = None
    
    def _setup_client(self):
        """Setup Facebook Graph API client"""
        try:
            import facebook
            
            if self.credentials.access_token:
                self.graph = facebook.GraphAPI(access_token=self.credentials.access_token)
                logger.info("Facebook Graph API client setup completed")
            else:
                logger.error("Facebook access token not provided")
                
        except Exception as e:
            logger.error(f"Failed to setup Facebook client: {e}")
            raise
    
    async def connect(self) -> bool:
        """Connect to Facebook"""
        try:
            if self.graph:
                # Test connection by getting user info
                me = self.graph.get_object('me')
                self.is_connected = True
                logger.info(f"Connected to Facebook as {me.get('name', 'Unknown')}")
                return True
            else:
                self.is_connected = False
                logger.error("No Facebook client available")
                return False
                
        except Exception as e:
            logger.error(f"Failed to connect to Facebook: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from Facebook"""
        self.is_connected = False
        logger.info("Disconnected from Facebook")
    
    async def post_content(self, content: GeneratedContent) -> Dict[str, Any]:
        """Post content to Facebook"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # Validate content
            if not self.validate_content(content):
                raise ValueError("Content validation failed")
            
            # Format content for Facebook
            formatted_text = self.format_content_for_platform(content)
            
            # Post to Facebook page or profile
            target_id = self.credentials.page_id or 'me'
            
            response = self.graph.put_object(
                parent_object=target_id,
                connection_name='feed',
                message=formatted_text
            )
            
            post_id = response['id']
            logger.info(f"Posted to Facebook with ID: {post_id}")
            
            return {
                "post_id": post_id,
                "platform": Platform.FACEBOOK,
                "status": "posted",
                "posted_at": datetime.utcnow(),
                "url": f"https://facebook.com/{post_id}"
            }
                
        except Exception as e:
            logger.error(f"Failed to post to Facebook: {e}")
            raise
    
    async def get_post_status(self, post_id: str) -> Dict[str, Any]:
        """Get the status of a Facebook post"""
        try:
            if not self.is_connected:
                await self.connect()
            
            post = self.graph.get_object(post_id)
            
            return {
                "post_id": post_id,
                "platform": Platform.FACEBOOK,
                "status": "posted",
                "text": post.get('message', ''),
                "created_at": post.get('created_time')
            }
            
        except Exception as e:
            logger.error(f"Failed to get Facebook post status: {e}")
            return {"post_id": post_id, "status": "error", "error": str(e)}
    
    async def get_engagement_metrics(self, post_id: str) -> Dict[str, Any]:
        """Get engagement metrics for a Facebook post"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # Get post insights
            insights = self.graph.get_object(
                f"{post_id}/insights",
                fields='impressions,reach,reactions,comments,shares'
            )
            
            metrics = {}
            for insight in insights.get('data', []):
                name = insight['name']
                value = insight['values'][0]['value'] if insight['values'] else 0
                metrics[name] = value
            
            return {
                "post_id": post_id,
                "platform": Platform.FACEBOOK,
                "likes": metrics.get('reactions', 0),
                "shares": metrics.get('shares', 0),
                "comments": metrics.get('comments', 0),
                "impressions": metrics.get('impressions', 0),
                "reach": metrics.get('reach', 0),
                "engagement_rate": 0.0  # Calculate based on reach
            }
            
        except Exception as e:
            logger.error(f"Failed to get Facebook engagement metrics: {e}")
            return {"post_id": post_id, "status": "error", "error": str(e)}
    
    async def delete_post(self, post_id: str) -> bool:
        """Delete a Facebook post"""
        try:
            if not self.is_connected:
                await self.connect()
            
            self.graph.delete_object(post_id)
            logger.info(f"Deleted Facebook post: {post_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete Facebook post: {e}")
            return False
    
    async def get_trending_topics(self) -> List[str]:
        """Get trending topics from Facebook (placeholder)"""
        # Facebook doesn't provide a public API for trending topics
        # This would need to be implemented with alternative data sources
        return ["#Facebook", "#SocialMedia", "#Trending", "#Viral"]
    
    def format_content_for_platform(self, content: GeneratedContent) -> str:
        """Format content specifically for Facebook"""
        formatted_text = content.text
        
        # Add hashtags
        if content.hashtags:
            hashtags_text = " ".join(content.hashtags)
            formatted_text += f"\n\n{hashtags_text}"
        
        return formatted_text
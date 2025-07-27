"""
AI Content Generator for Social Media Posts
"""

import asyncio
import random
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import feedparser
import requests
from bs4 import BeautifulSoup
from loguru import logger

from .config import config
from .models import ContentRequest, GeneratedContent, ContentType


class AIContentGenerator:
    """AI-powered content generator for social media posts"""
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self._setup_ai_clients()
        
    def _setup_ai_clients(self):
        """Initialize AI clients"""
        try:
            if config.ai.openai_api_key:
                import openai
                self.openai_client = openai.OpenAI(api_key=config.ai.openai_api_key)
                logger.info("OpenAI client initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI client: {e}")
            
        try:
            if config.ai.anthropic_api_key:
                import anthropic
                self.anthropic_client = anthropic.Anthropic(api_key=config.ai.anthropic_api_key)
                logger.info("Anthropic client initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Anthropic client: {e}")
    
    async def generate_content(self, request: ContentRequest) -> GeneratedContent:
        """Generate content based on the request"""
        try:
            # Get trending topics and news
            topics = await self._get_trending_topics()
            
            # Generate content using AI
            content = await self._generate_ai_content(request, topics)
            
            # Add hashtags
            hashtags = await self._generate_hashtags(content["text"], topics)
            
            # Create media content if requested
            media_urls = []
            if request.include_media:
                media_urls = await self._generate_media_content(content["text"])
            
            return GeneratedContent(
                text=content["text"],
                hashtags=hashtags,
                media_urls=media_urls,
                platform=request.platform,
                content_type=request.content_type,
                generated_at=datetime.utcnow(),
                ai_model=content["ai_model"]
            )
            
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            raise
    
    async def _get_trending_topics(self) -> List[str]:
        """Get trending topics from various sources"""
        topics = []
        
        # News API
        try:
            news_topics = await self._get_news_topics()
            topics.extend(news_topics)
        except Exception as e:
            logger.warning(f"Failed to get news topics: {e}")
        
        # RSS feeds
        try:
            rss_topics = await self._get_rss_topics()
            topics.extend(rss_topics)
        except Exception as e:
            logger.warning(f"Failed to get RSS topics: {e}")
        
        # Trending hashtags
        try:
            hashtag_topics = await self._get_trending_hashtags()
            topics.extend(hashtag_topics)
        except Exception as e:
            logger.warning(f"Failed to get trending hashtags: {e}")
        
        return list(set(topics))[:20]  # Limit to 20 unique topics
    
    async def _get_news_topics(self) -> List[str]:
        """Get trending topics from news sources"""
        topics = []
        
        # You can integrate with news APIs here
        # For now, using some default topics
        default_topics = [
            "artificial intelligence", "technology", "business", "health", 
            "environment", "science", "innovation", "startup", "digital transformation"
        ]
        
        return default_topics
    
    async def _get_rss_topics(self) -> List[str]:
        """Get topics from RSS feeds"""
        topics = []
        
        rss_feeds = [
            "https://feeds.bbci.co.uk/news/rss.xml",
            "https://rss.cnn.com/rss/edition.rss",
            "https://feeds.reuters.com/reuters/topNews"
        ]
        
        for feed_url in rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:5]:  # Get first 5 entries
                    # Extract keywords from title
                    words = entry.title.lower().split()
                    topics.extend([word for word in words if len(word) > 3])
            except Exception as e:
                logger.warning(f"Failed to parse RSS feed {feed_url}: {e}")
        
        return list(set(topics))
    
    async def _get_trending_hashtags(self) -> List[str]:
        """Get trending hashtags (placeholder for Twitter API integration)"""
        # This would integrate with Twitter API to get trending topics
        return ["#AI", "#Tech", "#Innovation", "#Business", "#Startup"]
    
    async def _generate_ai_content(self, request: ContentRequest, topics: List[str]) -> Dict:
        """Generate content using AI models"""
        topic = random.choice(topics) if topics else "technology"
        template = random.choice(config.ai.content_templates)
        prompt = template.format(topic=topic)
        
        # Add platform-specific instructions
        platform_instructions = self._get_platform_instructions(request.platform)
        full_prompt = f"{platform_instructions}\n\n{prompt}\n\nGenerate an engaging social media post."
        
        # Try OpenAI first, then Anthropic
        if self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model=config.ai.openai_model,
                    messages=[
                        {"role": "system", "content": "You are a social media expert who creates engaging, viral-worthy posts."},
                        {"role": "user", "content": full_prompt}
                    ],
                    max_tokens=config.ai.openai_max_tokens,
                    temperature=0.8
                )
                
                return {
                    "text": response.choices[0].message.content.strip(),
                    "ai_model": "openai"
                }
            except Exception as e:
                logger.warning(f"OpenAI generation failed: {e}")
        
        if self.anthropic_client:
            try:
                response = self.anthropic_client.messages.create(
                    model=config.ai.anthropic_model,
                    max_tokens=config.ai.openai_max_tokens,
                    messages=[
                        {"role": "user", "content": full_prompt}
                    ]
                )
                
                return {
                    "text": response.content[0].text.strip(),
                    "ai_model": "anthropic"
                }
            except Exception as e:
                logger.warning(f"Anthropic generation failed: {e}")
        
        # Fallback to template-based generation
        return {
            "text": f"Exciting news about {topic}! Stay tuned for more updates. #innovation #tech",
            "ai_model": "template"
        }
    
    def _get_platform_instructions(self, platform: str) -> str:
        """Get platform-specific instructions for content generation"""
        instructions = {
            "twitter": "Create a concise, engaging tweet under 280 characters. Use hashtags strategically.",
            "facebook": "Create a friendly, conversational post that encourages engagement and comments.",
            "linkedin": "Create a professional, thought-leadership style post with industry insights.",
            "instagram": "Create a visually descriptive post that works well with images.",
            "pinterest": "Create a descriptive, keyword-rich post that works well with pins."
        }
        
        return instructions.get(platform.lower(), "Create an engaging social media post.")
    
    async def _generate_hashtags(self, content: str, topics: List[str]) -> List[str]:
        """Generate relevant hashtags for the content"""
        hashtags = []
        
        # Extract keywords from content
        words = content.lower().split()
        keywords = [word for word in words if len(word) > 3 and word.isalpha()]
        
        # Add topic-based hashtags
        for topic in topics[:3]:
            hashtag = f"#{topic.replace(' ', '')}"
            hashtags.append(hashtag)
        
        # Add keyword-based hashtags
        for keyword in keywords[:2]:
            hashtag = f"#{keyword}"
            hashtags.append(hashtag)
        
        # Add trending hashtags
        trending = ["#AI", "#Innovation", "#Tech", "#Business"]
        hashtags.extend(trending[:2])
        
        return list(set(hashtags))[:config.ai.max_hashtags]
    
    async def _generate_media_content(self, content: str) -> List[str]:
        """Generate or find relevant media content"""
        # This would integrate with image generation APIs or stock photo services
        # For now, return placeholder URLs
        return [
            "https://example.com/generated-image-1.jpg",
            "https://example.com/generated-image-2.jpg"
        ]
    
    async def generate_content_batch(self, requests: List[ContentRequest]) -> List[GeneratedContent]:
        """Generate multiple content pieces in batch"""
        tasks = [self.generate_content(request) for request in requests]
        return await asyncio.gather(*tasks)
    
    def get_content_variations(self, base_content: str, count: int = 3) -> List[str]:
        """Generate variations of existing content"""
        variations = []
        
        # Simple template-based variations
        templates = [
            "💡 {content}",
            "🚀 {content}",
            "🔥 {content}",
            "✨ {content}",
            "🎯 {content}"
        ]
        
        for i in range(count):
            template = random.choice(templates)
            variation = template.format(content=base_content)
            variations.append(variation)
        
        return variations
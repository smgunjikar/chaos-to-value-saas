import asyncio
import random
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import json

import openai
import anthropic
from config.settings import settings, PLATFORM_CONFIGS
from models.database import DatabaseManager, ContentTemplate

logger = logging.getLogger(__name__)

class AIContentGenerator:
    """AI-powered content generation service"""
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        self.anthropic_client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.db = DatabaseManager()
        
        # Content generation prompts
        self.base_prompts = {
            "technology": {
                "system": "You are a technology expert and social media content creator. Create engaging, informative posts about the latest in tech, AI, startups, and innovation.",
                "topics": [
                    "Latest AI developments and breakthroughs",
                    "Startup success stories and lessons",
                    "Tech productivity tips and tools",
                    "Future of technology predictions",
                    "Programming and development insights",
                    "Cybersecurity awareness",
                    "Digital transformation trends"
                ]
            },
            "business": {
                "system": "You are a business strategist and thought leader. Create valuable content about entrepreneurship, leadership, business growth, and industry insights.",
                "topics": [
                    "Leadership lessons and strategies",
                    "Business growth tactics",
                    "Market trends and analysis",
                    "Entrepreneurship stories",
                    "Team building and management",
                    "Financial planning and investment",
                    "Customer experience insights"
                ]
            },
            "motivation": {
                "system": "You are an inspirational speaker and life coach. Create uplifting, motivational content that inspires action and positive thinking.",
                "topics": [
                    "Daily motivation and inspiration",
                    "Success mindset tips",
                    "Overcoming challenges and obstacles",
                    "Goal setting and achievement",
                    "Personal development insights",
                    "Work-life balance strategies",
                    "Building confidence and self-esteem"
                ]
            },
            "lifestyle": {
                "system": "You are a lifestyle influencer and wellness expert. Create content about health, productivity, personal growth, and living well.",
                "topics": [
                    "Health and wellness tips",
                    "Productivity hacks and systems",
                    "Travel experiences and tips",
                    "Food and nutrition insights",
                    "Home and lifestyle improvements",
                    "Mindfulness and mental health",
                    "Sustainable living practices"
                ]
            }
        }
    
    async def generate_content(self, platform: str, theme: str, 
                             include_hashtags: bool = True,
                             include_media_suggestions: bool = True) -> Dict[str, Any]:
        """Generate content for a specific platform and theme"""
        try:
            # Get platform configuration
            platform_config = PLATFORM_CONFIGS.get(platform, {})
            max_length = platform_config.get("max_text_length", 280)
            
            # Select random topic from theme
            theme_data = self.base_prompts.get(theme, self.base_prompts["technology"])
            topic = random.choice(theme_data["topics"])
            
            # Generate content using AI
            content = await self._generate_text_content(
                theme_data["system"], topic, platform, max_length
            )
            
            result = {
                "content": content,
                "platform": platform,
                "theme": theme,
                "topic": topic
            }
            
            # Generate hashtags if requested
            if include_hashtags:
                hashtags = await self._generate_hashtags(content, theme, platform)
                result["hashtags"] = hashtags
            
            # Generate media suggestions if requested
            if include_media_suggestions and platform_config.get("supports_images"):
                media_suggestions = await self._generate_media_suggestions(content, theme)
                result["media_suggestions"] = media_suggestions
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            return await self._get_fallback_content(platform, theme)
    
    async def _generate_text_content(self, system_prompt: str, topic: str, 
                                   platform: str, max_length: int) -> str:
        """Generate text content using AI"""
        # Create platform-specific prompt
        platform_instructions = {
            "twitter": "Create a concise, engaging tweet that sparks conversation and encourages retweets.",
            "instagram": "Create an Instagram caption that tells a story and connects with the audience emotionally.",
            "facebook": "Create a Facebook post that encourages discussion and community engagement.",
            "linkedin": "Create a professional LinkedIn post that provides value to your network.",
            "tiktok": "Create a short, catchy caption for a TikTok video that would go viral."
        }
        
        platform_instruction = platform_instructions.get(platform, platform_instructions["twitter"])
        
        prompt = f"""
        {system_prompt}
        
        Topic: {topic}
        Platform: {platform}
        
        Instructions:
        - {platform_instruction}
        - Maximum length: {max_length} characters
        - Be authentic, engaging, and valuable
        - Use a conversational tone
        - Include a call-to-action when appropriate
        - DO NOT include hashtags in the main text (they will be added separately)
        
        Generate the content now:
        """
        
        # Try OpenAI first, fallback to Anthropic
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.8
            )
            content = response.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"OpenAI failed, trying Anthropic: {str(e)}")
            try:
                response = await self.anthropic_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=200,
                    system=system_prompt,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text.strip()
            except Exception as e2:
                logger.error(f"Both AI services failed: {str(e2)}")
                raise e2
        
        # Ensure content fits within character limit
        if len(content) > max_length:
            content = content[:max_length-3] + "..."
        
        return content
    
    async def _generate_hashtags(self, content: str, theme: str, platform: str) -> List[str]:
        """Generate relevant hashtags for the content"""
        hashtag_counts = {
            "twitter": 3,
            "instagram": 10,
            "facebook": 5,
            "linkedin": 5,
            "tiktok": 8
        }
        
        max_hashtags = hashtag_counts.get(platform, 5)
        
        prompt = f"""
        Generate {max_hashtags} relevant hashtags for this {platform} post about {theme}:
        
        Content: {content}
        
        Requirements:
        - Hashtags should be relevant and popular
        - Mix of broad and specific hashtags
        - Include trending hashtags when relevant
        - Format: Return only hashtags separated by commas, without the # symbol
        
        Hashtags:
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.7
            )
            hashtags_text = response.choices[0].message.content.strip()
            hashtags = [tag.strip() for tag in hashtags_text.split(",") if tag.strip()]
            return hashtags[:max_hashtags]
        except Exception as e:
            logger.error(f"Error generating hashtags: {str(e)}")
            return self._get_default_hashtags(theme)[:max_hashtags]
    
    async def _generate_media_suggestions(self, content: str, theme: str) -> List[str]:
        """Generate media suggestions for the content"""
        prompt = f"""
        Suggest 3 types of visual content that would complement this post about {theme}:
        
        Content: {content}
        
        Provide suggestions for:
        1. Image type/style
        2. Video concept (if applicable)
        3. Graphic/infographic idea
        
        Keep suggestions brief and actionable.
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7
            )
            suggestions = response.choices[0].message.content.strip().split("\n")
            return [s.strip() for s in suggestions if s.strip()]
        except Exception as e:
            logger.error(f"Error generating media suggestions: {str(e)}")
            return []
    
    def _get_default_hashtags(self, theme: str) -> List[str]:
        """Get default hashtags for a theme"""
        default_hashtags = {
            "technology": ["tech", "innovation", "AI", "startup", "digital", "future", "techtrends"],
            "business": ["business", "entrepreneur", "leadership", "success", "growth", "strategy", "mindset"],
            "motivation": ["motivation", "inspiration", "success", "goals", "mindset", "growth", "positivity"],
            "lifestyle": ["lifestyle", "wellness", "health", "productivity", "life", "tips", "balance"]
        }
        return default_hashtags.get(theme, ["content", "social", "share"])
    
    async def _get_fallback_content(self, platform: str, theme: str) -> Dict[str, Any]:
        """Get fallback content when AI generation fails"""
        fallback_content = {
            "technology": [
                "The future is being built today. What technology trend excites you most?",
                "Innovation happens when creativity meets technology. What's your next big idea?",
                "Every expert was once a beginner. Keep learning, keep growing in tech!"
            ],
            "business": [
                "Success in business is about solving problems people didn't know they had.",
                "Great leaders don't create followers, they create more leaders.",
                "The best investment you can make is in yourself and your skills."
            ],
            "motivation": [
                "Your only limit is your mind. What will you achieve today?",
                "Success is not final, failure is not fatal. It's the courage to continue that counts.",
                "Dream big, start small, but most importantly - start today!"
            ],
            "lifestyle": [
                "Small daily improvements lead to stunning long-term results.",
                "Life is about balance. What brings you joy today?",
                "The best time to take care of yourself is now. What's one thing you'll do for yourself today?"
            ]
        }
        
        content = random.choice(fallback_content.get(theme, fallback_content["motivation"]))
        hashtags = self._get_default_hashtags(theme)[:5]
        
        return {
            "content": content,
            "platform": platform,
            "theme": theme,
            "topic": "fallback_content",
            "hashtags": hashtags,
            "media_suggestions": []
        }
    
    async def generate_batch_content(self, platforms: List[str], themes: List[str], 
                                   count_per_combination: int = 1) -> List[Dict[str, Any]]:
        """Generate multiple pieces of content for different platform/theme combinations"""
        tasks = []
        
        for platform in platforms:
            for theme in themes:
                for _ in range(count_per_combination):
                    task = self.generate_content(platform, theme)
                    tasks.append(task)
        
        # Execute all generation tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return valid results
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Content generation failed: {str(result)}")
            else:
                valid_results.append(result)
        
        return valid_results
    
    async def optimize_content_for_engagement(self, content: str, platform: str, 
                                            past_performance: Dict[str, Any] = None) -> str:
        """Optimize content based on past performance data"""
        if not past_performance:
            return content
        
        optimization_prompt = f"""
        Optimize this {platform} post for better engagement based on performance data:
        
        Original content: {content}
        
        Performance insights:
        - Best performing content themes: {past_performance.get('top_themes', [])}
        - Average engagement rate: {past_performance.get('avg_engagement', 0)}%
        - Best posting times: {past_performance.get('best_times', [])}
        
        Improve the content while maintaining its core message and staying within character limits.
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": optimization_prompt}],
                max_tokens=200,
                temperature=0.7
            )
            optimized_content = response.choices[0].message.content.strip()
            
            # Ensure it still fits the platform's character limit
            max_length = PLATFORM_CONFIGS.get(platform, {}).get("max_text_length", 280)
            if len(optimized_content) > max_length:
                optimized_content = optimized_content[:max_length-3] + "..."
            
            return optimized_content
        except Exception as e:
            logger.error(f"Error optimizing content: {str(e)}")
            return content  # Return original if optimization fails
    
    def close(self):
        """Clean up resources"""
        self.db.close()
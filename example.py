#!/usr/bin/env python3
"""
Example usage of the AI Social Media Agent
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.ai_agent import AISocialMediaAgent
from src.models import Platform, ContentRequest
from src.config import config


async def example_basic_usage():
    """Basic usage example"""
    print("🤖 AI Social Media Agent - Basic Usage Example")
    print("=" * 50)
    
    # Create agent instance
    agent = AISocialMediaAgent()
    
    # Get agent status
    status = await agent.get_status()
    print(f"Agent Status: {'Running' if status.is_running else 'Stopped'}")
    print(f"Active Platforms: {len(status.active_platforms)}")
    print(f"Total Posts Today: {status.total_posts_today}")
    print(f"Successful Posts: {status.successful_posts}")
    print(f"Failed Posts: {status.failed_posts}")
    
    # Get platform health
    print("\n📊 Platform Health:")
    for platform_name, platform in agent.platforms.items():
        health = await platform.health_check()
        status_emoji = "✅" if health["status"] == "healthy" else "❌"
        print(f"  {status_emoji} {platform_name.value}: {health['status']}")


async def example_manual_posting():
    """Manual posting example"""
    print("\n📝 Manual Posting Example")
    print("=" * 30)
    
    agent = AISocialMediaAgent()
    
    # Example content for different platforms
    content_examples = {
        Platform.TWITTER: "Exciting news about AI technology! 🚀 #AI #Tech #Innovation",
        Platform.FACEBOOK: "What do you think about the latest developments in artificial intelligence? Share your thoughts below! 🤔",
        Platform.LINKEDIN: "The future of business is being shaped by AI. Here's what you need to know about digital transformation.",
        Platform.INSTAGRAM: "✨ Amazing AI innovations that are changing the world! #AI #Innovation #Future",
        Platform.PINTEREST: "Discover the latest AI trends and innovations! #AI #Technology #Innovation"
    }
    
    for platform, content in content_examples.items():
        if platform in agent.platforms:
            try:
                print(f"\n📤 Posting to {platform.value}...")
                result = await agent.manual_post(
                    platform=platform,
                    content=content,
                    include_media=False
                )
                print(f"  ✅ Success! Post ID: {result.get('post_id', 'N/A')}")
            except Exception as e:
                print(f"  ❌ Failed: {e}")


async def example_content_generation():
    """Content generation example"""
    print("\n🎨 Content Generation Example")
    print("=" * 35)
    
    from src.ai_content_generator import AIContentGenerator
    
    generator = AIContentGenerator()
    
    # Generate content for different platforms
    platforms = [Platform.TWITTER, Platform.FACEBOOK, Platform.LINKEDIN]
    topics = ["artificial intelligence", "technology", "innovation", "startup", "digital transformation"]
    
    for platform in platforms:
        for topic in topics[:2]:  # Just use first 2 topics for demo
            try:
                print(f"\n🎯 Generating content for {platform.value} about {topic}...")
                
                request = ContentRequest(
                    platform=platform,
                    topic=topic,
                    include_media=False
                )
                
                content = await generator.generate_content(request)
                
                print(f"  📝 Generated Text: {content.text[:100]}...")
                print(f"  🏷️  Hashtags: {', '.join(content.hashtags)}")
                print(f"  🤖 AI Model: {content.ai_model}")
                
            except Exception as e:
                print(f"  ❌ Failed: {e}")


async def example_analytics():
    """Analytics example"""
    print("\n📈 Analytics Example")
    print("=" * 25)
    
    agent = AISocialMediaAgent()
    
    # Get posting metrics
    metrics = await agent.get_posting_metrics(days=7)
    
    print("📊 7-Day Posting Metrics:")
    for platform, metric in metrics.items():
        print(f"  📱 {platform}:")
        print(f"    - Posts Posted: {metric.posts_posted}")
        print(f"    - Posts Failed: {metric.posts_failed}")
        print(f"    - Total Engagement: {metric.total_engagement}")
        print(f"    - Avg Engagement Rate: {metric.avg_engagement_rate:.2f}%")
    
    # Get analytics
    print("\n📊 Overall Analytics:")
    analytics = await agent.get_analytics()
    print(f"  📝 Total Posts: {analytics['total_posts']}")
    print(f"  ✅ Successful Posts: {analytics['successful_posts']}")
    print(f"  ❌ Failed Posts: {analytics['failed_posts']}")
    print(f"  📊 Success Rate: {analytics['success_rate']:.1f}%")
    print(f"  🎯 Total Engagement: {analytics['total_engagement']}")


async def example_scheduling():
    """Scheduling example"""
    print("\n⏰ Scheduling Example")
    print("=" * 25)
    
    print("Current Scheduling Configuration:")
    print(f"  📅 Posting Hours: {config.scheduling.posting_start_hour}:00 - {config.scheduling.posting_end_hour}:00")
    print(f"  ⏱️  Min Interval: {config.scheduling.min_interval} minutes")
    print(f"  ⏱️  Max Interval: {config.scheduling.max_interval} minutes")
    print(f"  📊 Max Daily Posts: {config.scheduling.max_daily_posts}")
    print(f"  🌍 Timezone: {config.scheduling.timezone}")
    
    print("\n📋 Scheduled Tasks:")
    print("  🔄 Hourly posting job")
    print("  🎨 Content generation every 6 hours")
    print("  📊 Analytics collection every 2 hours")
    print("  🏥 Health checks every 30 minutes")


def main():
    """Main example function"""
    print("🚀 AI Social Media Agent Examples")
    print("=" * 40)
    
    async def run_examples():
        await example_basic_usage()
        await example_content_generation()
        await example_analytics()
        await example_scheduling()
        
        # Note: Manual posting example is commented out to avoid actual posting
        # await example_manual_posting()
        print("\n⚠️  Manual posting example skipped to avoid actual posting")
        print("   Uncomment the line in main() to test manual posting")
    
    # Run examples
    asyncio.run(run_examples())
    
    print("\n✅ Examples completed!")
    print("\n📚 Next Steps:")
    print("  1. Configure your .env file with API credentials")
    print("  2. Run 'python main.py' to start the agent")
    print("  3. Run 'python -m src.api' to start the web interface")
    print("  4. Visit http://localhost:8000/docs for API documentation")


if __name__ == "__main__":
    main()
import asyncio
import logging
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import schedule
import time
from threading import Thread
import signal
import sys

from services.ai_content_generator import AIContentGenerator
from services.social_media_platforms import SocialMediaManager
from models.database import DatabaseManager, Post
from config.settings import settings

logger = logging.getLogger(__name__)

class PostScheduler:
    """24/7 automated posting scheduler"""
    
    def __init__(self):
        self.ai_generator = AIContentGenerator()
        self.social_manager = SocialMediaManager()
        self.db = DatabaseManager()
        self.is_running = False
        self.scheduler_thread = None
        
        # Track posting history to avoid spam
        self.posting_history = {}
        
        # Available platforms
        self.platforms = ["twitter", "facebook", "instagram", "linkedin", "tiktok"]
        
        # Optimal posting times for each platform (hour of day)
        self.optimal_times = {
            "twitter": [8, 12, 17, 20],  # 8am, 12pm, 5pm, 8pm
            "facebook": [9, 13, 15, 19],  # 9am, 1pm, 3pm, 7pm
            "instagram": [11, 14, 17, 19],  # 11am, 2pm, 5pm, 7pm
            "linkedin": [8, 12, 14, 17],  # 8am, 12pm, 2pm, 5pm
            "tiktok": [16, 18, 20, 22]  # 4pm, 6pm, 8pm, 10pm
        }
    
    async def initialize(self):
        """Initialize the scheduler"""
        try:
            # Authenticate with all platforms
            auth_results = await self.social_manager.authenticate_all()
            authenticated_platforms = [platform for platform, success in auth_results.items() if success]
            
            if not authenticated_platforms:
                logger.error("No platforms authenticated successfully!")
                return False
            
            logger.info(f"Authenticated platforms: {authenticated_platforms}")
            self.platforms = authenticated_platforms
            
            # Setup posting schedules
            self._setup_schedules()
            
            return True
            
        except Exception as e:
            logger.error(f"Error initializing scheduler: {str(e)}")
            return False
    
    def _setup_schedules(self):
        """Setup posting schedules for all platforms"""
        # Clear existing schedules
        schedule.clear()
        
        # Create schedules for each platform and theme combination
        for platform in self.platforms:
            for theme in settings.content_themes:
                # Schedule posts at optimal times
                optimal_hours = self.optimal_times.get(platform, [9, 15, 21])
                
                for hour in optimal_hours:
                    # Add some randomness to avoid posting at exact same times
                    minute = random.randint(0, 59)
                    
                    schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(
                        self._schedule_post_sync, platform, theme
                    )
        
        # Schedule content generation (runs more frequently)
        schedule.every(30).minutes.do(self._generate_content_batch_sync)
        
        # Schedule analytics collection
        schedule.every(2).hours.do(self._collect_analytics_sync)
        
        # Schedule cleanup tasks
        schedule.every().day.at("02:00").do(self._cleanup_old_data_sync)
        
        logger.info(f"Scheduled {len(schedule.jobs)} recurring tasks")
    
    def _schedule_post_sync(self, platform: str, theme: str):
        """Synchronous wrapper for scheduling posts"""
        asyncio.run(self._schedule_post(platform, theme))
    
    def _generate_content_batch_sync(self):
        """Synchronous wrapper for batch content generation"""
        asyncio.run(self._generate_content_batch())
    
    def _collect_analytics_sync(self):
        """Synchronous wrapper for analytics collection"""
        asyncio.run(self._collect_analytics())
    
    def _cleanup_old_data_sync(self):
        """Synchronous wrapper for cleanup tasks"""
        asyncio.run(self._cleanup_old_data())
    
    async def _schedule_post(self, platform: str, theme: str):
        """Schedule a post for a specific platform and theme"""
        try:
            # Check if we should post (rate limiting)
            if not self._should_post(platform):
                logger.debug(f"Skipping post for {platform} due to rate limiting")
                return
            
            # Check for existing scheduled posts
            scheduled_posts = self.db.get_scheduled_posts(limit=1)
            
            if scheduled_posts:
                # Use existing scheduled post
                post = scheduled_posts[0]
                await self._execute_post(post)
            else:
                # Generate new content and post immediately
                content_data = await self.ai_generator.generate_content(platform, theme)
                if content_data:
                    await self._create_and_execute_post(content_data)
            
        except Exception as e:
            logger.error(f"Error scheduling post for {platform}/{theme}: {str(e)}")
    
    async def _generate_content_batch(self):
        """Generate a batch of content for future posting"""
        try:
            # Generate content for all platform/theme combinations
            content_batch = await self.ai_generator.generate_batch_content(
                platforms=self.platforms,
                themes=settings.content_themes,
                count_per_combination=2  # Generate 2 posts per combination
            )
            
            # Schedule posts for optimal times
            for content_data in content_batch:
                scheduled_time = self._get_next_optimal_time(content_data["platform"])
                
                post = self.db.create_post(
                    content=content_data["content"],
                    platform=content_data["platform"],
                    theme=content_data["theme"],
                    hashtags=content_data.get("hashtags", []),
                    scheduled_time=scheduled_time
                )
                
                # Set status to scheduled
                self.db.update_post_status(post.id, "scheduled")
            
            logger.info(f"Generated and scheduled {len(content_batch)} posts")
            
        except Exception as e:
            logger.error(f"Error generating content batch: {str(e)}")
    
    async def _create_and_execute_post(self, content_data: Dict[str, Any]):
        """Create a post in database and execute it immediately"""
        try:
            # Create post in database
            post = self.db.create_post(
                content=content_data["content"],
                platform=content_data["platform"],
                theme=content_data["theme"],
                hashtags=content_data.get("hashtags", []),
                scheduled_time=datetime.now()
            )
            
            # Execute the post
            await self._execute_post(post)
            
        except Exception as e:
            logger.error(f"Error creating and executing post: {str(e)}")
    
    async def _execute_post(self, post: Post):
        """Execute a scheduled post"""
        try:
            # Post to the platform
            result = await self.social_manager.post_to_platform(
                platform_name=post.platform,
                content=post.content,
                hashtags=post.hashtags
            )
            
            # Update post status based on result
            if result.get("success"):
                self.db.update_post_status(
                    post.id,
                    "posted",
                    platform_post_id=result.get("platform_post_id")
                )
                
                # Update posting history
                self._update_posting_history(post.platform)
                
                logger.info(f"Successfully posted to {post.platform}: {post.content[:50]}...")
            else:
                self.db.update_post_status(
                    post.id,
                    "failed",
                    error_message=result.get("error", "Unknown error")
                )
                logger.error(f"Failed to post to {post.platform}: {result.get('error')}")
            
        except Exception as e:
            logger.error(f"Error executing post {post.id}: {str(e)}")
            self.db.update_post_status(post.id, "failed", error_message=str(e))
    
    async def _collect_analytics(self):
        """Collect analytics for recent posts"""
        try:
            # Get posts from last 24 hours that were successfully posted
            posts = self.db.session.query(Post).filter(
                Post.status == "posted",
                Post.posted_time >= datetime.now() - timedelta(hours=24),
                Post.platform_post_id.isnot(None)
            ).all()
            
            for post in posts:
                try:
                    analytics = await self.social_manager.get_analytics_for_post(
                        post.platform, post.platform_post_id
                    )
                    
                    if analytics:
                        self.db.record_analytics(post.id, post.platform, analytics)
                        
                except Exception as e:
                    logger.error(f"Error collecting analytics for post {post.id}: {str(e)}")
            
            if posts:
                logger.info(f"Collected analytics for {len(posts)} posts")
                
        except Exception as e:
            logger.error(f"Error in analytics collection: {str(e)}")
    
    async def _cleanup_old_data(self):
        """Clean up old data and temporary files"""
        try:
            # Delete failed posts older than 7 days
            cutoff_date = datetime.now() - timedelta(days=7)
            
            old_posts = self.db.session.query(Post).filter(
                Post.status == "failed",
                Post.created_at < cutoff_date
            ).all()
            
            for post in old_posts:
                self.db.session.delete(post)
            
            self.db.session.commit()
            
            if old_posts:
                logger.info(f"Cleaned up {len(old_posts)} old failed posts")
            
        except Exception as e:
            logger.error(f"Error in cleanup: {str(e)}")
    
    def _should_post(self, platform: str) -> bool:
        """Check if we should post to a platform (rate limiting)"""
        now = datetime.now()
        platform_history = self.posting_history.get(platform, [])
        
        # Remove posts older than 24 hours
        platform_history = [
            post_time for post_time in platform_history
            if now - post_time < timedelta(hours=24)
        ]
        
        # Update history
        self.posting_history[platform] = platform_history
        
        # Check if we've exceeded daily limit
        return len(platform_history) < settings.max_posts_per_day
    
    def _update_posting_history(self, platform: str):
        """Update posting history for a platform"""
        if platform not in self.posting_history:
            self.posting_history[platform] = []
        
        self.posting_history[platform].append(datetime.now())
    
    def _get_next_optimal_time(self, platform: str) -> datetime:
        """Get the next optimal posting time for a platform"""
        now = datetime.now()
        optimal_hours = self.optimal_times.get(platform, [9, 15, 21])
        
        # Find next optimal hour
        current_hour = now.hour
        next_hour = None
        
        for hour in optimal_hours:
            if hour > current_hour:
                next_hour = hour
                break
        
        if next_hour is None:
            # No more optimal times today, use first optimal time tomorrow
            next_hour = optimal_hours[0]
            now = now + timedelta(days=1)
        
        # Add some randomness
        minute = random.randint(0, 59)
        
        return now.replace(hour=next_hour, minute=minute, second=0, microsecond=0)
    
    def start(self):
        """Start the 24/7 scheduler"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        self.is_running = True
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Start scheduler in a separate thread
        self.scheduler_thread = Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("24/7 Post Scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.is_running = False
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        # Clean up resources
        self.ai_generator.close()
        self.db.close()
        
        logger.info("Post Scheduler stopped")
    
    def _run_scheduler(self):
        """Main scheduler loop"""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in scheduler loop: {str(e)}")
                time.sleep(60)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()
        sys.exit(0)
    
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        return {
            "is_running": self.is_running,
            "authenticated_platforms": [name for name, platform in self.social_manager.platforms.items() if platform.is_authenticated],
            "scheduled_jobs": len(schedule.jobs),
            "posting_history": {
                platform: len(history) for platform, history in self.posting_history.items()
            },
            "next_jobs": [
                {
                    "job": str(job.job_func),
                    "next_run": job.next_run.isoformat() if job.next_run else None
                }
                for job in sorted(schedule.jobs, key=lambda x: x.next_run or datetime.max)[:5]
            ]
        }

class InteractiveScheduler:
    """Interactive scheduler for manual control"""
    
    def __init__(self):
        self.scheduler = PostScheduler()
    
    async def run_interactive(self):
        """Run interactive mode"""
        print("🚀 AI Social Media Agent - Interactive Mode")
        print("=" * 50)
        
        # Initialize scheduler
        if not await self.scheduler.initialize():
            print("❌ Failed to initialize scheduler")
            return
        
        while True:
            print("\nOptions:")
            print("1. Start 24/7 scheduler")
            print("2. Generate and post content now")
            print("3. View scheduler status")
            print("4. View recent posts")
            print("5. Exit")
            
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == "1":
                self.scheduler.start()
                print("✅ 24/7 scheduler started!")
                print("Press Ctrl+C to stop")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    self.scheduler.stop()
                    print("\n✅ Scheduler stopped")
            
            elif choice == "2":
                await self._manual_post()
            
            elif choice == "3":
                self._show_status()
            
            elif choice == "4":
                self._show_recent_posts()
            
            elif choice == "5":
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please try again.")
    
    async def _manual_post(self):
        """Manually generate and post content"""
        print("\nGenerating content...")
        
        # Get available platforms
        platforms = list(self.scheduler.social_manager.platforms.keys())
        
        print("Available platforms:")
        for i, platform in enumerate(platforms, 1):
            print(f"{i}. {platform.title()}")
        
        try:
            platform_choice = int(input(f"Choose platform (1-{len(platforms)}): ")) - 1
            if platform_choice < 0 or platform_choice >= len(platforms):
                raise ValueError()
            
            platform = platforms[platform_choice]
            
            print("Available themes:")
            for i, theme in enumerate(settings.content_themes, 1):
                print(f"{i}. {theme.title()}")
            
            theme_choice = int(input(f"Choose theme (1-{len(settings.content_themes)}): ")) - 1
            if theme_choice < 0 or theme_choice >= len(settings.content_themes):
                raise ValueError()
            
            theme = settings.content_themes[theme_choice]
            
            # Generate content
            content_data = await self.scheduler.ai_generator.generate_content(platform, theme)
            
            if content_data:
                print(f"\n📝 Generated content:")
                print(f"Platform: {content_data['platform'].title()}")
                print(f"Theme: {content_data['theme'].title()}")
                print(f"Content: {content_data['content']}")
                if content_data.get('hashtags'):
                    print(f"Hashtags: {', '.join(['#' + tag for tag in content_data['hashtags']])}")
                
                confirm = input("\nPost this content? (y/n): ").strip().lower()
                if confirm == 'y':
                    await self.scheduler._create_and_execute_post(content_data)
                    print("✅ Content posted!")
                else:
                    print("❌ Post cancelled")
            else:
                print("❌ Failed to generate content")
                
        except ValueError:
            print("❌ Invalid choice")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    def _show_status(self):
        """Show scheduler status"""
        status = self.scheduler.get_status()
        
        print("\n📊 Scheduler Status")
        print("=" * 30)
        print(f"Running: {'✅ Yes' if status['is_running'] else '❌ No'}")
        print(f"Authenticated platforms: {', '.join(status['authenticated_platforms'])}")
        print(f"Scheduled jobs: {status['scheduled_jobs']}")
        print(f"Posts today: {status['posting_history']}")
        
        if status['next_jobs']:
            print("\nNext scheduled jobs:")
            for job in status['next_jobs'][:3]:
                print(f"- {job['job']}: {job['next_run']}")
    
    def _show_recent_posts(self):
        """Show recent posts"""
        try:
            recent_posts = self.scheduler.db.session.query(Post).order_by(
                Post.created_at.desc()
            ).limit(10).all()
            
            if recent_posts:
                print("\n📱 Recent Posts")
                print("=" * 50)
                for post in recent_posts:
                    status_emoji = "✅" if post.status == "posted" else "❌" if post.status == "failed" else "⏳"
                    print(f"{status_emoji} {post.platform.title()} | {post.theme} | {post.content[:50]}...")
                    print(f"   Created: {post.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                    if post.status == "failed" and post.error_message:
                        print(f"   Error: {post.error_message}")
                    print()
            else:
                print("No recent posts found")
                
        except Exception as e:
            print(f"❌ Error fetching posts: {str(e)}")

# Example usage
async def main():
    """Main function for running the scheduler"""
    interactive = InteractiveScheduler()
    await interactive.run_interactive()

if __name__ == "__main__":
    asyncio.run(main())
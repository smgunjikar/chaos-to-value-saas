#!/usr/bin/env python3
"""
AI Social Media Agent
A 24/7 automated social media posting system that generates and posts content
across multiple platforms using AI.
"""

import asyncio
import logging
import argparse
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('social_agent.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def setup_environment():
    """Setup the environment and check requirements"""
    try:
        # Check if .env file exists
        env_file = Path('.env')
        if not env_file.exists():
            logger.warning("No .env file found. Please copy .env.example to .env and configure your API keys.")
            return False
        
        # Create necessary directories
        Path('logs').mkdir(exist_ok=True)
        Path('media').mkdir(exist_ok=True)
        Path('temp').mkdir(exist_ok=True)
        
        return True
        
    except Exception as e:
        logger.error(f"Error setting up environment: {str(e)}")
        return False

async def run_cli_mode():
    """Run the CLI interactive mode"""
    from services.scheduler import InteractiveScheduler
    
    logger.info("Starting AI Social Media Agent in CLI mode")
    
    scheduler = InteractiveScheduler()
    await scheduler.run_interactive()

async def run_daemon_mode():
    """Run the 24/7 daemon mode"""
    from services.scheduler import PostScheduler
    from models.database import create_tables
    
    logger.info("Starting AI Social Media Agent in daemon mode")
    
    # Create database tables
    create_tables()
    
    # Initialize and start scheduler
    scheduler = PostScheduler()
    
    if await scheduler.initialize():
        logger.info("Scheduler initialized successfully")
        scheduler.start()
        
        try:
            # Keep the daemon running
            while True:
                await asyncio.sleep(60)
                
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down...")
            scheduler.stop()
    else:
        logger.error("Failed to initialize scheduler")
        sys.exit(1)

def run_web_dashboard():
    """Run the web dashboard"""
    from api.web_dashboard import create_app
    import uvicorn
    
    logger.info("Starting AI Social Media Agent web dashboard")
    
    app = create_app()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

def run_api_server():
    """Run the API server"""
    from api.main import create_app
    import uvicorn
    
    logger.info("Starting AI Social Media Agent API server")
    
    app = create_app()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )

async def generate_sample_content():
    """Generate and display sample content"""
    from services.ai_content_generator import AIContentGenerator
    from config.settings import settings
    
    logger.info("Generating sample content...")
    
    generator = AIContentGenerator()
    
    try:
        # Generate content for each platform and theme
        platforms = ["twitter", "facebook", "instagram", "linkedin"]
        themes = settings.content_themes
        
        print("\n🎨 Sample Generated Content")
        print("=" * 60)
        
        for platform in platforms:
            for theme in themes:
                try:
                    content_data = await generator.generate_content(platform, theme)
                    
                    print(f"\n📱 {platform.upper()} - {theme.upper()}")
                    print("-" * 40)
                    print(f"Content: {content_data['content']}")
                    if content_data.get('hashtags'):
                        print(f"Hashtags: {', '.join(['#' + tag for tag in content_data['hashtags']])}")
                    print()
                    
                except Exception as e:
                    print(f"❌ Error generating content for {platform}/{theme}: {str(e)}")
        
    except Exception as e:
        logger.error(f"Error in sample content generation: {str(e)}")
    finally:
        generator.close()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="AI Social Media Agent - 24/7 Automated Social Media Posting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --mode cli          # Run interactive CLI mode
  %(prog)s --mode daemon       # Run 24/7 daemon mode
  %(prog)s --mode web          # Run web dashboard
  %(prog)s --mode api          # Run API server
  %(prog)s --sample            # Generate sample content
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['cli', 'daemon', 'web', 'api'],
        default='cli',
        help='Run mode (default: cli)'
    )
    
    parser.add_argument(
        '--sample',
        action='store_true',
        help='Generate and display sample content'
    )
    
    parser.add_argument(
        '--setup',
        action='store_true',
        help='Setup the environment and database'
    )
    
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup verbose logging if requested
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Setup environment
    if not setup_environment():
        logger.error("Environment setup failed")
        sys.exit(1)
    
    # Handle setup command
    if args.setup:
        from models.database import create_tables
        try:
            create_tables()
            print("✅ Database tables created successfully")
            return
        except Exception as e:
            print(f"❌ Error creating database tables: {str(e)}")
            sys.exit(1)
    
    # Handle sample content generation
    if args.sample:
        asyncio.run(generate_sample_content())
        return
    
    # Run the selected mode
    try:
        if args.mode == 'cli':
            asyncio.run(run_cli_mode())
        elif args.mode == 'daemon':
            asyncio.run(run_daemon_mode())
        elif args.mode == 'web':
            run_web_dashboard()
        elif args.mode == 'api':
            run_api_server()
            
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
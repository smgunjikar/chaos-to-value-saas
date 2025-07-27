#!/usr/bin/env python3
"""
AI Social Media Agent - 24/7 Automated Social Media Posting System
Main entry point
"""

import asyncio
import signal
import sys
from pathlib import Path
from loguru import logger

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.ai_agent import AISocialMediaAgent
from src.config import config


def setup_logging():
    """Setup logging configuration"""
    logger.remove()  # Remove default handler
    
    # Add console handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=config.monitoring.log_level,
        colorize=True
    )
    
    # Add file handler
    logger.add(
        "logs/ai_agent.log",
        rotation="1 day",
        retention="30 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=config.monitoring.log_level
    )


async def main():
    """Main application entry point"""
    try:
        # Setup logging
        setup_logging()
        
        logger.info("Starting AI Social Media Agent...")
        logger.info(f"Environment: {config.environment}")
        logger.info(f"Debug mode: {config.debug}")
        
        # Create and start the AI agent
        agent = AISocialMediaAgent()
        
        # Setup signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down gracefully...")
            asyncio.create_task(agent.stop())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start the agent
        await agent.start()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    Path("logs").mkdir(exist_ok=True)
    
    # Run the main application
    asyncio.run(main())
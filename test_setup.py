#!/usr/bin/env python3
"""
Test script to verify AI Social Media Agent setup
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from src.config import config
        print("  ✅ Config module imported")
    except Exception as e:
        print(f"  ❌ Config module failed: {e}")
        return False
    
    try:
        from src.models import Platform, ContentRequest, GeneratedContent
        print("  ✅ Models module imported")
    except Exception as e:
        print(f"  ❌ Models module failed: {e}")
        return False
    
    try:
        from src.ai_content_generator import AIContentGenerator
        print("  ✅ AI Content Generator imported")
    except Exception as e:
        print(f"  ❌ AI Content Generator failed: {e}")
        return False
    
    try:
        from src.platforms import TwitterPlatform, FacebookPlatform
        print("  ✅ Platform modules imported")
    except Exception as e:
        print(f"  ❌ Platform modules failed: {e}")
        return False
    
    try:
        from src.ai_agent import AISocialMediaAgent
        print("  ✅ AI Agent imported")
    except Exception as e:
        print(f"  ❌ AI Agent failed: {e}")
        return False
    
    return True


def test_config():
    """Test configuration loading"""
    print("\n⚙️  Testing configuration...")
    
    try:
        from src.config import config
        
        print(f"  📋 Environment: {config.environment}")
        print(f"  🐛 Debug mode: {config.debug}")
        print(f"  📅 Timezone: {config.scheduling.timezone}")
        print(f"  ⏰ Posting hours: {config.scheduling.posting_start_hour}-{config.scheduling.posting_end_hour}")
        print(f"  📊 Max daily posts: {config.scheduling.max_daily_posts}")
        
        # Check if any AI services are configured
        ai_configured = bool(config.ai.openai_api_key or config.ai.anthropic_api_key)
        print(f"  🤖 AI services configured: {ai_configured}")
        
        # Check if any platforms are configured
        platforms_configured = bool(
            config.social_media.twitter_api_key or
            config.social_media.facebook_access_token or
            config.social_media.linkedin_access_token or
            config.social_media.instagram_username or
            config.social_media.pinterest_access_token
        )
        print(f"  📱 Platforms configured: {platforms_configured}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Configuration test failed: {e}")
        return False


async def test_agent_creation():
    """Test agent creation"""
    print("\n🤖 Testing agent creation...")
    
    try:
        from src.ai_agent import AISocialMediaAgent
        
        agent = AISocialMediaAgent()
        print(f"  ✅ Agent created successfully")
        print(f"  📱 Configured platforms: {len(agent.platforms)}")
        
        # Test status
        status = await agent.get_status()
        print(f"  📊 Agent status: {'Running' if status.is_running else 'Stopped'}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Agent creation failed: {e}")
        return False


async def test_content_generation():
    """Test content generation"""
    print("\n🎨 Testing content generation...")
    
    try:
        from src.ai_content_generator import AIContentGenerator
        from src.models import ContentRequest, Platform
        
        generator = AIContentGenerator()
        
        # Test content generation
        request = ContentRequest(
            platform=Platform.TWITTER,
            topic="artificial intelligence",
            include_media=False
        )
        
        content = await generator.generate_content(request)
        print(f"  ✅ Content generated successfully")
        print(f"  📝 Text length: {len(content.text)} characters")
        print(f"  🏷️  Hashtags: {len(content.hashtags)}")
        print(f"  🤖 AI model: {content.ai_model}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Content generation failed: {e}")
        return False


def test_web_api():
    """Test web API setup"""
    print("\n🌐 Testing web API...")
    
    try:
        from src.api import app
        print("  ✅ FastAPI app created successfully")
        
        # Test that we can get the app info
        print(f"  📋 App title: {app.title}")
        print(f"  📋 App version: {app.version}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Web API test failed: {e}")
        return False


async def main():
    """Main test function"""
    print("🧪 AI Social Media Agent - Setup Test")
    print("=" * 45)
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_config),
        ("Agent Creation Test", test_agent_creation),
        ("Content Generation Test", test_content_generation),
        ("Web API Test", test_web_api),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
            else:
                print(f"  ❌ {test_name} failed")
                
        except Exception as e:
            print(f"  ❌ {test_name} failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Setup is ready.")
        print("\n📚 Next steps:")
        print("  1. Configure your .env file with API credentials")
        print("  2. Run './start.sh' to start the agent")
        print("  3. Run 'python -m src.api' to start the web interface")
        print("  4. Visit http://localhost:8000/docs for API documentation")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("  1. Make sure all dependencies are installed: pip install -r requirements.txt")
        print("  2. Check that your .env file is properly configured")
        print("  3. Verify that all required API credentials are set")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime, timedelta

from services.scheduler import PostScheduler
from services.ai_content_generator import AIContentGenerator
from services.social_media_platforms import SocialMediaManager
from models.database import DatabaseManager, Post
from config.settings import settings

def create_app() -> FastAPI:
    """Create and configure the FastAPI web dashboard application"""
    
    app = FastAPI(
        title="AI Social Media Agent Dashboard",
        description="Manage your 24/7 AI social media posting agent",
        version="1.0.0"
    )
    
    # Setup templates and static files
    templates = Jinja2Templates(directory="templates")
    
    # Create static directory if it doesn't exist
    import os
    os.makedirs("static", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    
    try:
        app.mount("/static", StaticFiles(directory="static"), name="static")
    except:
        pass  # Static directory might not exist yet
    
    # Global instances
    scheduler = PostScheduler()
    db = DatabaseManager()
    
    @app.on_event("startup")
    async def startup_event():
        """Initialize the application on startup"""
        await scheduler.initialize()
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Cleanup on shutdown"""
        scheduler.stop()
        db.close()
    
    @app.get("/", response_class=HTMLResponse)
    async def dashboard(request: Request):
        """Main dashboard page"""
        # Get dashboard data
        status = scheduler.get_status()
        stats = db.get_performance_stats(days=7)
        
        # Get recent posts
        recent_posts = db.session.query(Post).order_by(
            Post.created_at.desc()
        ).limit(10).all()
        
        # Calculate success rate
        total_posts = stats.get("total_posts", 0)
        successful_posts = stats.get("successful_posts", 0)
        success_rate = (successful_posts / total_posts * 100) if total_posts > 0 else 0
        
        dashboard_data = {
            "status": status,
            "stats": stats,
            "recent_posts": recent_posts,
            "success_rate": round(success_rate, 1),
            "platforms": list(scheduler.social_manager.platforms.keys()),
            "themes": settings.content_themes
        }
        
        return templates.TemplateResponse(
            "dashboard.html",
            {"request": request, **dashboard_data}
        )
    
    @app.post("/scheduler/start")
    async def start_scheduler():
        """Start the 24/7 scheduler"""
        try:
            if not scheduler.is_running:
                scheduler.start()
                return {"success": True, "message": "Scheduler started successfully"}
            else:
                return {"success": False, "message": "Scheduler is already running"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/scheduler/stop")
    async def stop_scheduler():
        """Stop the scheduler"""
        try:
            if scheduler.is_running:
                scheduler.stop()
                return {"success": True, "message": "Scheduler stopped successfully"}
            else:
                return {"success": False, "message": "Scheduler is not running"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/status")
    async def get_status():
        """Get scheduler status"""
        return scheduler.get_status()
    
    @app.get("/api/stats")
    async def get_stats(days: int = 7):
        """Get performance statistics"""
        return db.get_performance_stats(days=days)
    
    @app.get("/api/posts")
    async def get_posts(limit: int = 50):
        """Get recent posts"""
        posts = db.session.query(Post).order_by(
            Post.created_at.desc()
        ).limit(limit).all()
        
        return [
            {
                "id": post.id,
                "content": post.content,
                "platform": post.platform,
                "theme": post.theme,
                "status": post.status,
                "created_at": post.created_at.isoformat(),
                "posted_time": post.posted_time.isoformat() if post.posted_time else None,
                "hashtags": post.hashtags,
                "error_message": post.error_message
            }
            for post in posts
        ]
    
    @app.post("/api/generate-content")
    async def generate_content(platform: str = Form(...), theme: str = Form(...)):
        """Generate content for a specific platform and theme"""
        try:
            ai_generator = AIContentGenerator()
            content_data = await ai_generator.generate_content(platform, theme)
            ai_generator.close()
            
            if content_data:
                return {"success": True, "content_data": content_data}
            else:
                return {"success": False, "message": "Failed to generate content"}
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/post-content")
    async def post_content(
        platform: str = Form(...),
        content: str = Form(...),
        hashtags: str = Form(default="")
    ):
        """Post content to a specific platform"""
        try:
            # Parse hashtags
            hashtag_list = [tag.strip().replace("#", "") for tag in hashtags.split(",") if tag.strip()]
            
            # Create post in database
            post = db.create_post(
                content=content,
                platform=platform,
                hashtags=hashtag_list,
                scheduled_time=datetime.now()
            )
            
            # Execute the post
            await scheduler._execute_post(post)
            
            return {"success": True, "message": "Content posted successfully", "post_id": post.id}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/content", response_class=HTMLResponse)
    async def content_page(request: Request):
        """Content generation and management page"""
        return templates.TemplateResponse(
            "content.html",
            {
                "request": request,
                "platforms": list(scheduler.social_manager.platforms.keys()),
                "themes": settings.content_themes
            }
        )
    
    @app.get("/analytics", response_class=HTMLResponse)
    async def analytics_page(request: Request):
        """Analytics and reporting page"""
        # Get analytics data
        stats = db.get_performance_stats(days=30)
        
        # Get platform-specific stats
        platform_stats = {}
        for platform in scheduler.social_manager.platforms.keys():
            platform_stats[platform] = db.get_performance_stats(platform=platform, days=30)
        
        return templates.TemplateResponse(
            "analytics.html",
            {
                "request": request,
                "stats": stats,
                "platform_stats": platform_stats
            }
        )
    
    @app.get("/settings", response_class=HTMLResponse)
    async def settings_page(request: Request):
        """Settings and configuration page"""
        return templates.TemplateResponse(
            "settings.html",
            {
                "request": request,
                "current_settings": {
                    "content_themes": settings.content_themes,
                    "post_frequency_hours": settings.post_frequency_hours,
                    "max_posts_per_day": settings.max_posts_per_day,
                    "content_variation": settings.content_variation
                }
            }
        )
    
    return app

# Template content (since we can't create separate template files in this environment)
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Social Media Agent Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-gray-100">
    <div class="min-h-screen">
        <!-- Navigation -->
        <nav class="bg-blue-600 text-white p-4">
            <div class="container mx-auto flex justify-between items-center">
                <h1 class="text-2xl font-bold">🤖 AI Social Media Agent</h1>
                <div class="flex space-x-4">
                    <a href="/" class="hover:bg-blue-700 px-3 py-2 rounded">Dashboard</a>
                    <a href="/content" class="hover:bg-blue-700 px-3 py-2 rounded">Content</a>
                    <a href="/analytics" class="hover:bg-blue-700 px-3 py-2 rounded">Analytics</a>
                    <a href="/settings" class="hover:bg-blue-700 px-3 py-2 rounded">Settings</a>
                </div>
            </div>
        </nav>

        <div class="container mx-auto p-6">
            <!-- Status Cards -->
            <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <div class="bg-white rounded-lg shadow p-6">
                    <div class="flex items-center">
                        <div class="p-3 rounded-full bg-green-100 text-green-800">
                            <i class="fas fa-play"></i>
                        </div>
                        <div class="ml-4">
                            <p class="text-sm text-gray-600">Status</p>
                            <p class="text-lg font-semibold">
                                {{ "✅ Running" if status.is_running else "❌ Stopped" }}
                            </p>
                        </div>
                    </div>
                </div>

                <div class="bg-white rounded-lg shadow p-6">
                    <div class="flex items-center">
                        <div class="p-3 rounded-full bg-blue-100 text-blue-800">
                            <i class="fas fa-share-alt"></i>
                        </div>
                        <div class="ml-4">
                            <p class="text-sm text-gray-600">Posts This Week</p>
                            <p class="text-lg font-semibold">{{ stats.total_posts }}</p>
                        </div>
                    </div>
                </div>

                <div class="bg-white rounded-lg shadow p-6">
                    <div class="flex items-center">
                        <div class="p-3 rounded-full bg-purple-100 text-purple-800">
                            <i class="fas fa-chart-line"></i>
                        </div>
                        <div class="ml-4">
                            <p class="text-sm text-gray-600">Success Rate</p>
                            <p class="text-lg font-semibold">{{ success_rate }}%</p>
                        </div>
                    </div>
                </div>

                <div class="bg-white rounded-lg shadow p-6">
                    <div class="flex items-center">
                        <div class="p-3 rounded-full bg-orange-100 text-orange-800">
                            <i class="fas fa-network-wired"></i>
                        </div>
                        <div class="ml-4">
                            <p class="text-sm text-gray-600">Platforms</p>
                            <p class="text-lg font-semibold">{{ status.authenticated_platforms|length }}</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Control Panel -->
            <div class="bg-white rounded-lg shadow p-6 mb-8">
                <h2 class="text-xl font-semibold mb-4">Control Panel</h2>
                <div class="flex space-x-4">
                    <button onclick="toggleScheduler()" 
                            class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded">
                        {{ "Stop Scheduler" if status.is_running else "Start Scheduler" }}
                    </button>
                    <button onclick="generateContent()" 
                            class="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded">
                        Generate Content
                    </button>
                    <button onclick="refreshData()" 
                            class="bg-gray-600 hover:bg-gray-700 text-white px-6 py-2 rounded">
                        <i class="fas fa-sync-alt"></i> Refresh
                    </button>
                </div>
            </div>

            <!-- Recent Posts -->
            <div class="bg-white rounded-lg shadow p-6">
                <h2 class="text-xl font-semibold mb-4">Recent Posts</h2>
                <div class="overflow-x-auto">
                    <table class="min-w-full table-auto">
                        <thead>
                            <tr class="bg-gray-50">
                                <th class="px-4 py-2 text-left">Platform</th>
                                <th class="px-4 py-2 text-left">Content</th>
                                <th class="px-4 py-2 text-left">Status</th>
                                <th class="px-4 py-2 text-left">Created</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for post in recent_posts %}
                            <tr class="border-t">
                                <td class="px-4 py-2">
                                    <span class="inline-block bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                                        {{ post.platform.title() }}
                                    </span>
                                </td>
                                <td class="px-4 py-2">{{ post.content[:100] }}...</td>
                                <td class="px-4 py-2">
                                    {% if post.status == "posted" %}
                                        <span class="text-green-600">✅ Posted</span>
                                    {% elif post.status == "failed" %}
                                        <span class="text-red-600">❌ Failed</span>
                                    {% else %}
                                        <span class="text-yellow-600">⏳ {{ post.status.title() }}</span>
                                    {% endif %}
                                </td>
                                <td class="px-4 py-2 text-sm text-gray-600">
                                    {{ post.created_at.strftime('%Y-%m-%d %H:%M') }}
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script>
        async function toggleScheduler() {
            const action = {{ "stop" if status.is_running else "start" }};
            try {
                const response = await fetch(`/scheduler/${action}`, { method: 'POST' });
                const result = await response.json();
                alert(result.message);
                location.reload();
            } catch (error) {
                alert('Error: ' + error.message);
            }
        }

        function generateContent() {
            window.location.href = '/content';
        }

        function refreshData() {
            location.reload();
        }

        // Auto-refresh every 30 seconds
        setInterval(() => {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    // Update status indicators
                    console.log('Status updated:', data);
                });
        }, 30000);
    </script>
</body>
</html>
"""

# Create templates directory and write the template
import os
os.makedirs("templates", exist_ok=True)

with open("templates/dashboard.html", "w") as f:
    f.write(DASHBOARD_TEMPLATE)

# Create a simple content generation template
CONTENT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Content Generation - AI Social Media Agent</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-gray-100">
    <div class="min-h-screen">
        <!-- Navigation -->
        <nav class="bg-blue-600 text-white p-4">
            <div class="container mx-auto flex justify-between items-center">
                <h1 class="text-2xl font-bold">🤖 AI Social Media Agent</h1>
                <div class="flex space-x-4">
                    <a href="/" class="hover:bg-blue-700 px-3 py-2 rounded">Dashboard</a>
                    <a href="/content" class="bg-blue-700 px-3 py-2 rounded">Content</a>
                    <a href="/analytics" class="hover:bg-blue-700 px-3 py-2 rounded">Analytics</a>
                    <a href="/settings" class="hover:bg-blue-700 px-3 py-2 rounded">Settings</a>
                </div>
            </div>
        </nav>

        <div class="container mx-auto p-6">
            <h1 class="text-3xl font-bold mb-8">Content Generation</h1>
            
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <!-- Content Generator -->
                <div class="bg-white rounded-lg shadow p-6">
                    <h2 class="text-xl font-semibold mb-4">Generate New Content</h2>
                    <form onsubmit="generateContent(event)">
                        <div class="mb-4">
                            <label class="block text-sm font-medium text-gray-700 mb-2">Platform</label>
                            <select name="platform" required class="w-full p-3 border border-gray-300 rounded-lg">
                                {% for platform in platforms %}
                                <option value="{{ platform }}">{{ platform.title() }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        
                        <div class="mb-4">
                            <label class="block text-sm font-medium text-gray-700 mb-2">Theme</label>
                            <select name="theme" required class="w-full p-3 border border-gray-300 rounded-lg">
                                {% for theme in themes %}
                                <option value="{{ theme }}">{{ theme.title() }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        
                        <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 px-4 rounded-lg">
                            <i class="fas fa-magic"></i> Generate Content
                        </button>
                    </form>
                </div>

                <!-- Generated Content Display -->
                <div class="bg-white rounded-lg shadow p-6">
                    <h2 class="text-xl font-semibold mb-4">Generated Content</h2>
                    <div id="generated-content" class="hidden">
                        <div class="mb-4">
                            <label class="block text-sm font-medium text-gray-700 mb-2">Content</label>
                            <textarea id="content-text" class="w-full p-3 border border-gray-300 rounded-lg h-32" readonly></textarea>
                        </div>
                        
                        <div class="mb-4">
                            <label class="block text-sm font-medium text-gray-700 mb-2">Hashtags</label>
                            <input type="text" id="hashtags-text" class="w-full p-3 border border-gray-300 rounded-lg" readonly>
                        </div>
                        
                        <button onclick="postContent()" class="w-full bg-green-600 hover:bg-green-700 text-white py-3 px-4 rounded-lg">
                            <i class="fas fa-share"></i> Post Now
                        </button>
                    </div>
                    
                    <div id="loading" class="hidden text-center py-8">
                        <i class="fas fa-spinner fa-spin text-3xl text-blue-600"></i>
                        <p class="mt-2 text-gray-600">Generating content...</p>
                    </div>
                    
                    <div id="placeholder" class="text-center py-8 text-gray-500">
                        <i class="fas fa-lightbulb text-3xl"></i>
                        <p class="mt-2">Select platform and theme to generate content</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let generatedData = null;

        async function generateContent(event) {
            event.preventDefault();
            
            const form = event.target;
            const formData = new FormData(form);
            
            // Show loading state
            document.getElementById('placeholder').classList.add('hidden');
            document.getElementById('generated-content').classList.add('hidden');
            document.getElementById('loading').classList.remove('hidden');
            
            try {
                const response = await fetch('/api/generate-content', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    generatedData = result.content_data;
                    
                    // Display generated content
                    document.getElementById('content-text').value = result.content_data.content;
                    document.getElementById('hashtags-text').value = result.content_data.hashtags ? 
                        result.content_data.hashtags.map(tag => '#' + tag).join(', ') : '';
                    
                    document.getElementById('loading').classList.add('hidden');
                    document.getElementById('generated-content').classList.remove('hidden');
                } else {
                    alert('Failed to generate content: ' + result.message);
                    document.getElementById('loading').classList.add('hidden');
                    document.getElementById('placeholder').classList.remove('hidden');
                }
            } catch (error) {
                alert('Error: ' + error.message);
                document.getElementById('loading').classList.add('hidden');
                document.getElementById('placeholder').classList.remove('hidden');
            }
        }

        async function postContent() {
            if (!generatedData) return;
            
            const formData = new FormData();
            formData.append('platform', generatedData.platform);
            formData.append('content', generatedData.content);
            formData.append('hashtags', generatedData.hashtags ? generatedData.hashtags.join(', ') : '');
            
            try {
                const response = await fetch('/api/post-content', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alert('Content posted successfully!');
                    // Reset the form
                    document.getElementById('generated-content').classList.add('hidden');
                    document.getElementById('placeholder').classList.remove('hidden');
                    generatedData = null;
                } else {
                    alert('Failed to post content: ' + result.message);
                }
            } catch (error) {
                alert('Error posting content: ' + error.message);
            }
        }
    </script>
</body>
</html>
"""

with open("templates/content.html", "w") as f:
    f.write(CONTENT_TEMPLATE)
# 🤖 AI Social Media Agent

A 24/7 automated social media posting system that uses AI to generate and post engaging content across multiple platforms including Twitter/X, Instagram, Facebook, LinkedIn, and TikTok.

## 🌟 Features

- **24/7 Automated Posting**: Continuously generates and posts content around the clock
- **Multi-Platform Support**: Posts to Twitter/X, Instagram, Facebook, LinkedIn, and TikTok
- **AI-Powered Content Generation**: Uses OpenAI GPT-4 and Anthropic Claude for creating engaging content
- **Smart Scheduling**: Posts at optimal times for each platform to maximize engagement
- **Content Themes**: Supports multiple themes including technology, business, motivation, and lifestyle
- **Analytics Tracking**: Monitors post performance and engagement metrics
- **Web Dashboard**: Beautiful web interface for monitoring and control
- **Rate Limiting**: Respects platform limits and avoids spam
- **Hashtag Generation**: Automatically generates relevant hashtags for each post
- **Media Support**: Handles images and videos (when available)
- **Fallback Systems**: Continues working even if AI services are temporarily unavailable

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd ai-social-media-agent

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Copy the environment file and configure your API keys:

```bash
cp .env.example .env
```

Edit `.env` file with your API keys and credentials:

```env
# AI Service Configuration
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Twitter/X Configuration
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
TWITTER_BEARER_TOKEN=your_twitter_bearer_token

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/social_media_agent
REDIS_URL=redis://localhost:6379

# ... (see .env.example for all options)
```

### 3. Database Setup

```bash
# Setup database tables
python main.py --setup
```

### 4. Run the Application

Choose one of the following modes:

#### Interactive CLI Mode (Recommended for first-time setup)
```bash
python main.py --mode cli
```

#### 24/7 Daemon Mode
```bash
python main.py --mode daemon
```

#### Web Dashboard
```bash
python main.py --mode web
# Access at http://localhost:8000
```

#### API Server
```bash
python main.py --mode api
# Access at http://localhost:8080
```

## 📋 Requirements

### API Keys Required

1. **OpenAI API Key** - For content generation
   - Get from: https://platform.openai.com/api-keys
   - Used for: GPT-4 content generation and hashtag creation

2. **Anthropic API Key** - Backup content generation
   - Get from: https://console.anthropic.com/
   - Used for: Claude content generation as fallback

3. **Twitter/X API Keys** - For Twitter posting
   - Get from: https://developer.twitter.com/
   - Required: API Key, API Secret, Access Token, Access Token Secret, Bearer Token

4. **Facebook API Keys** - For Facebook posting
   - Get from: https://developers.facebook.com/
   - Required: Access Token, Page ID

5. **Instagram Credentials** - For Instagram posting
   - Username and Password required
   - Note: Consider using Instagram Business API for production

6. **LinkedIn API Keys** - For LinkedIn posting
   - Get from: https://www.linkedin.com/developers/
   - Required: Client ID, Client Secret, Access Token

### Database Requirements

- **PostgreSQL** - Primary database for storing posts and analytics
- **Redis** - For caching and task queuing (optional but recommended)

### System Requirements

- Python 3.8+
- Linux/macOS/Windows
- 2GB+ RAM
- Stable internet connection

## 🎛️ Configuration Options

### Content Settings

```env
# Themes for content generation
CONTENT_THEMES=technology,business,motivation,lifestyle

# Posting frequency
POST_FREQUENCY_HOURS=4
MAX_POSTS_PER_DAY=6

# Content variation level
CONTENT_VARIATION=high
```

### Platform-Specific Limits

The system automatically respects each platform's limits:

- **Twitter**: 280 characters, 4 images max
- **Instagram**: 2200 characters, 10 images max, requires media
- **Facebook**: ~63K characters, 20 images max
- **LinkedIn**: 3000 characters, 9 images max
- **TikTok**: 150 characters, videos only

## 🖥️ Usage

### CLI Commands

```bash
# Generate sample content without posting
python main.py --sample

# Setup database
python main.py --setup

# Run with verbose logging
python main.py --mode cli --verbose

# Run different modes
python main.py --mode cli      # Interactive mode
python main.py --mode daemon   # 24/7 background mode
python main.py --mode web      # Web dashboard
python main.py --mode api      # API server only
```

### Web Dashboard Features

1. **Dashboard**: Overview of status, statistics, and recent posts
2. **Content Generation**: Manual content creation and posting
3. **Analytics**: Performance metrics and engagement tracking
4. **Settings**: Configuration management

### API Endpoints

```
GET  /api/status              # Get scheduler status
GET  /api/stats               # Get performance statistics
GET  /api/posts               # Get recent posts
POST /api/generate-content    # Generate new content
POST /api/post-content        # Post content to platform
POST /scheduler/start         # Start the scheduler
POST /scheduler/stop          # Stop the scheduler
```

## 🏗️ Architecture

```
├── main.py                          # Application entry point
├── config/
│   └── settings.py                  # Configuration management
├── models/
│   └── database.py                  # Database models and operations
├── services/
│   ├── ai_content_generator.py      # AI content generation
│   ├── social_media_platforms.py    # Platform integrations
│   └── scheduler.py                 # 24/7 scheduling system
├── api/
│   └── web_dashboard.py             # Web interface
└── templates/                       # HTML templates
```

## 🔧 Advanced Configuration

### Custom Content Templates

Add custom content templates to the database:

```python
from models.database import DatabaseManager, ContentTemplate

db = DatabaseManager()
template = ContentTemplate(
    name="Tech Tip Template",
    template="💡 Tech Tip: {tip}\n\nWhat's your experience with this? {cta}",
    platform="twitter",
    theme="technology",
    variables=["tip", "cta"]
)
db.session.add(template)
db.session.commit()
```

### Custom Posting Schedule

Modify optimal posting times in `services/scheduler.py`:

```python
self.optimal_times = {
    "twitter": [8, 12, 17, 20],    # Customize these hours
    "facebook": [9, 13, 15, 19],
    # ... etc
}
```

### Analytics Integration

The system automatically tracks:
- Post engagement (likes, shares, comments)
- Platform performance
- Success/failure rates
- Optimal posting times

## 🚨 Important Notes

### Platform Terms of Service

- **Instagram**: Username/password login may violate ToS. Consider Instagram Business API for production.
- **LinkedIn**: Unofficial API usage may have limitations.
- **TikTok**: Official API requires special approval.

### Rate Limiting

The system includes built-in rate limiting to prevent:
- Posting too frequently
- Exceeding platform limits
- Getting accounts suspended

### Content Quality

- AI-generated content is reviewed before posting
- Fallback content is available if AI services fail
- Content is tailored to each platform's requirements

## 🛠️ Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Verify API keys in `.env` file
   - Check API key permissions and quotas
   - Ensure tokens haven't expired

2. **Database Connection Issues**
   - Verify PostgreSQL is running
   - Check database credentials in `.env`
   - Run `python main.py --setup` to create tables

3. **Content Generation Failures**
   - Check OpenAI API quota and billing
   - Verify Anthropic API key as backup
   - Review logs for specific error messages

4. **Platform Posting Failures**
   - Check platform API status
   - Verify account permissions
   - Review platform-specific requirements

### Logs

Check logs for detailed error information:
- Application logs: `social_agent.log`
- Console output: Run with `--verbose` flag

## 📈 Performance Optimization

### Database Optimization

- Use PostgreSQL for better performance
- Add database indexes for frequently queried fields
- Regularly clean up old posts and analytics data

### Memory Usage

- The system is designed to be memory-efficient
- Redis can help with caching frequently used data
- Consider using database connection pooling for high-volume usage

### API Rate Limiting

- Built-in rate limiting prevents API quota exhaustion
- Customize posting frequency based on your API limits
- Monitor API usage in platform dashboards

## 🔒 Security

### API Key Security

- Never commit API keys to version control
- Use environment variables for all sensitive data
- Regularly rotate API keys
- Use separate API keys for development and production

### Database Security

- Use strong database passwords
- Enable SSL connections for production
- Regularly backup your database
- Limit database access to necessary IPs only

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is for educational and legitimate business purposes only. Users are responsible for:
- Complying with platform terms of service
- Respecting intellectual property rights
- Following applicable laws and regulations
- Using the tool ethically and responsibly

The creators are not responsible for any misuse of this software or any consequences resulting from its use.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the logs for error details
3. Open an issue on GitHub with detailed information
4. Include your configuration (without API keys) and error logs

---

**Happy Posting! 🚀**

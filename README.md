# AI Social Media Agent - 24/7 Automated Social Media Posting

A sophisticated AI-powered social media agent that automatically generates and posts content across multiple platforms 24/7. Built with Python, FastAPI, and modern AI technologies.

## 🚀 Features

### Core Features
- **24/7 Automated Posting**: Continuously generates and posts content across all configured platforms
- **Multi-Platform Support**: Twitter/X, Facebook, LinkedIn, Instagram, Pinterest
- **AI-Powered Content Generation**: Uses OpenAI GPT-4 and Anthropic Claude for intelligent content creation
- **Smart Scheduling**: Configurable posting intervals and time windows
- **Trending Topic Integration**: Automatically incorporates trending topics and hashtags
- **Content Variety**: Generates different types of content (text, images, videos)
- **Engagement Analytics**: Tracks likes, shares, comments, and engagement rates
- **Health Monitoring**: Real-time platform health checks and status monitoring

### Advanced Features
- **Retry Logic**: Automatic retry with exponential backoff for failed posts
- **Content Validation**: Platform-specific content validation and formatting
- **Rate Limiting**: Respects platform rate limits and API quotas
- **Error Handling**: Comprehensive error handling and logging
- **Web Dashboard**: FastAPI-based web interface for monitoring and control
- **REST API**: Full REST API for integration with other systems
- **Metrics Collection**: Detailed analytics and performance metrics

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Redis (for caching and session management)
- Social media API credentials

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ai-social-media-agent
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory:

```env
# Environment
ENVIRONMENT=development
DEBUG=false

# AI Services
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_MODEL=gpt-4
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Twitter/X Configuration
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
TWITTER_BEARER_TOKEN=your_twitter_bearer_token

# Facebook Configuration
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
FACEBOOK_ACCESS_TOKEN=your_facebook_access_token
FACEBOOK_PAGE_ID=your_facebook_page_id

# LinkedIn Configuration
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token

# Instagram Configuration
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password

# Pinterest Configuration
PINTEREST_ACCESS_TOKEN=your_pinterest_access_token
PINTEREST_BOARD_ID=your_pinterest_board_id

# Scheduling Configuration
MIN_POSTING_INTERVAL=60
MAX_POSTING_INTERVAL=240
POSTING_START_HOUR=8
POSTING_END_HOUR=22
MAX_DAILY_POSTS=10

# Monitoring Configuration
LOG_LEVEL=INFO
ENABLE_METRICS=true
METRICS_PORT=8000
```

### 4. Platform Setup

#### Twitter/X
1. Create a Twitter Developer account
2. Create a new app and get API credentials
3. Generate access tokens with appropriate permissions
4. Add credentials to `.env` file

#### Facebook
1. Create a Facebook Developer account
2. Create a new app
3. Generate a page access token
4. Add credentials to `.env` file

#### LinkedIn
1. Create a LinkedIn Developer account
2. Create a new app
3. Generate access tokens
4. Add credentials to `.env` file

#### Instagram
1. Use Instagram Basic Display API
2. Generate access tokens
3. Add credentials to `.env` file

#### Pinterest
1. Create a Pinterest Developer account
2. Generate access tokens
3. Add credentials to `.env` file

## 🚀 Usage

### 1. Start the AI Agent
```bash
python main.py
```

### 2. Start the Web Interface
```bash
python -m src.api
```

### 3. Access the Web Dashboard
Open your browser and navigate to:
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Status**: http://localhost:8000/status

## 📊 API Endpoints

### Core Endpoints
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /status` - Agent status
- `POST /start` - Start the agent
- `POST /stop` - Stop the agent

### Platform Management
- `GET /platforms` - List configured platforms
- `GET /platforms/{platform}/health` - Platform health check

### Content Management
- `POST /post/manual` - Manual post to specific platform
- `GET /posts` - Get posting history
- `GET /metrics` - Get posting metrics
- `GET /analytics` - Get analytics data

### Configuration
- `GET /config` - Get current configuration

## 🔧 Configuration

### Scheduling Options
- **Posting Intervals**: Configure minimum and maximum intervals between posts
- **Time Windows**: Set active posting hours
- **Daily Limits**: Set maximum posts per day
- **Content Types**: Configure which types of content to generate

### AI Configuration
- **Models**: Choose between OpenAI GPT-4 and Anthropic Claude
- **Content Templates**: Customize content generation prompts
- **Hashtag Strategy**: Configure hashtag generation and limits
- **Tone and Style**: Set content tone and target audience

### Platform Settings
- **Rate Limits**: Configure platform-specific rate limiting
- **Content Validation**: Set platform-specific content rules
- **Error Handling**: Configure retry strategies and error thresholds

## 📈 Monitoring and Analytics

### Real-time Metrics
- **Posting Success Rate**: Track successful vs failed posts
- **Engagement Metrics**: Monitor likes, shares, comments
- **Platform Performance**: Compare performance across platforms
- **Content Performance**: Identify best-performing content types

### Health Monitoring
- **Platform Status**: Real-time platform connectivity status
- **API Quotas**: Monitor API usage and rate limits
- **Error Tracking**: Track and analyze posting errors
- **Uptime Monitoring**: Monitor agent uptime and performance

## 🔒 Security

### API Security
- **Environment Variables**: All sensitive data stored in environment variables
- **Token Management**: Secure token storage and rotation
- **Rate Limiting**: Built-in rate limiting to prevent API abuse
- **Error Logging**: Secure error logging without exposing sensitive data

### Platform Security
- **OAuth Integration**: Proper OAuth flow for all platforms
- **Token Refresh**: Automatic token refresh when needed
- **Secure Storage**: Encrypted storage of platform credentials

## 🚀 Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

### Production Deployment
1. Set up a production server
2. Configure environment variables
3. Set up Redis for caching
4. Configure logging and monitoring
5. Set up SSL certificates
6. Configure firewall rules

### Monitoring Setup
- **Log Aggregation**: Set up centralized logging
- **Metrics Collection**: Configure metrics collection
- **Alerting**: Set up alerts for failures and issues
- **Backup**: Regular backup of configuration and data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Common Issues

#### Platform Connection Issues
- Verify API credentials are correct
- Check platform API status
- Ensure proper permissions are granted
- Verify rate limits are not exceeded

#### Content Generation Issues
- Check AI API keys are valid
- Verify API quotas are not exceeded
- Check content validation rules
- Review error logs for specific issues

#### Scheduling Issues
- Verify timezone configuration
- Check posting window settings
- Review daily post limits
- Check platform-specific restrictions

### Getting Help
- Check the logs in `logs/ai_agent.log`
- Review the API documentation at `/docs`
- Check platform-specific documentation
- Open an issue on GitHub

## 🔮 Future Enhancements

### Planned Features
- **Advanced Analytics**: Machine learning-powered content optimization
- **A/B Testing**: Automated content testing and optimization
- **Image Generation**: AI-powered image generation for posts
- **Video Content**: Automated video content creation
- **Influencer Integration**: Connect with influencer networks
- **Advanced Scheduling**: AI-powered optimal posting time detection
- **Multi-language Support**: Content generation in multiple languages
- **Advanced Monitoring**: Real-time dashboard with charts and graphs

### Platform Expansions
- **TikTok**: TikTok API integration
- **YouTube**: YouTube Shorts posting
- **Reddit**: Reddit community engagement
- **Discord**: Discord server integration
- **Telegram**: Telegram channel posting

---

**Note**: This AI agent is designed for legitimate social media marketing purposes. Please ensure compliance with all platform terms of service and applicable laws when using this tool.

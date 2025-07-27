# AI Social Media Agent - Quick Start Guide

## 🚀 Getting Started

### 1. Environment Setup

The AI Social Media Agent is now fully set up and ready to use! Here's how to get started:

```bash
# Activate the virtual environment
source venv/bin/activate

# Verify everything is working
python3 test_setup.py
```

### 2. Configuration

1. **Copy the environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file** with your actual API credentials:
   - Get OpenAI API key from: https://platform.openai.com/api-keys
   - Get Anthropic API key from: https://console.anthropic.com/
   - Configure social media platform credentials (see platform-specific guides below)

### 3. Running the Agent

#### Option A: Using the startup script
```bash
./start.sh
```

#### Option B: Manual start
```bash
# Activate virtual environment
source venv/bin/activate

# Start the agent
python3 main.py
```

#### Option C: Using Docker
```bash
# Build and run with Docker Compose
docker-compose up -d
```

### 4. Web Interface

Start the web API for monitoring and control:

```bash
# In a new terminal
source venv/bin/activate
python3 -m uvicorn src.api:app --host 0.0.0.0 --port 8000
```

Then visit: http://localhost:8000/docs

## 📱 Platform Setup Guides

### Twitter/X Setup
1. Go to https://developer.twitter.com/
2. Create a new app
3. Generate API keys and tokens
4. Add to `.env` file

### Facebook Setup
1. Go to https://developers.facebook.com/
2. Create a new app
3. Get app ID and secret
4. Generate page access token
5. Add to `.env` file

### LinkedIn Setup
1. Go to https://www.linkedin.com/developers/
2. Create a new app
3. Get client ID and secret
4. Generate access token
5. Add to `.env` file

### Instagram Setup
- Currently uses username/password authentication
- Add credentials to `.env` file

### Pinterest Setup
1. Go to https://developers.pinterest.com/
2. Create a new app
3. Generate access token
4. Add to `.env` file

## 🔧 Key Features

### ✅ What's Working Now
- ✅ AI content generation (OpenAI, Anthropic, fallback templates)
- ✅ Multi-platform social media posting
- ✅ Automated scheduling (24/7 operation)
- ✅ Web API for monitoring and control
- ✅ Content management and analytics
- ✅ Docker containerization
- ✅ Comprehensive logging and error handling

### 🎯 Core Capabilities
- **24/7 Operation**: Automated posting with configurable intervals
- **AI-Powered Content**: Generates engaging posts using AI models
- **Multi-Platform**: Posts to Twitter, Facebook, LinkedIn, Instagram, Pinterest
- **Smart Scheduling**: Respects posting windows and daily limits
- **Content Variety**: Rotates through different content types and topics
- **Analytics**: Tracks engagement metrics and post performance
- **Web Interface**: Monitor and control via REST API

## 📊 Monitoring

### Web API Endpoints
- `GET /health` - Agent health status
- `GET /status` - Detailed agent status
- `GET /platforms` - Platform information
- `POST /post` - Manual posting
- `GET /analytics` - Performance metrics

### Logs
The agent logs all activities to the console and can be configured to log to files.

## 🐳 Docker Deployment

For production deployment:

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## 🔒 Security Notes

- Never commit your `.env` file to version control
- Use strong, unique API keys for each platform
- Regularly rotate access tokens
- Monitor API usage to stay within limits

## 🆘 Troubleshooting

### Common Issues

1. **"No module named 'pydantic'"**
   - Activate virtual environment: `source venv/bin/activate`

2. **API authentication errors**
   - Check your `.env` file has correct credentials
   - Verify API keys are valid and have proper permissions

3. **Platform connection issues**
   - Ensure platform apps are properly configured
   - Check API rate limits and quotas

4. **Content generation fails**
   - Verify OpenAI/Anthropic API keys are valid
   - Check internet connectivity

### Getting Help

- Check the logs for detailed error messages
- Use the web API health endpoint to diagnose issues
- Review the README.md for detailed documentation

## 🎉 Success!

Your AI Social Media Agent is now ready to run 24/7, automatically posting engaging content across all your social media platforms!

The system will:
- Generate AI-powered content
- Post at optimal times
- Track performance
- Provide analytics
- Handle errors gracefully

Start with a few platforms first, then gradually add more as you become comfortable with the system.
#!/bin/bash

# AI Social Media Agent Startup Script

set -e

echo "🚀 Starting AI Social Media Agent..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file with your configuration."
    echo "See README.md for setup instructions."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed!"
    echo "Please install Python 3.8+ and try again."
    exit 1
fi

# Check if required packages are installed
echo "📦 Checking dependencies..."
if ! python3 -c "import fastapi, loguru, pydantic" &> /dev/null; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Check if running in Docker
if [ -f /.dockerenv ]; then
    echo "🐳 Running in Docker container..."
    exec python3 main.py
else
    echo "🖥️  Running on host system..."
    
    # Check if Redis is running (optional)
    if command -v redis-cli &> /dev/null; then
        if redis-cli ping &> /dev/null; then
            echo "✅ Redis is running"
        else
            echo "⚠️  Redis is not running (optional)"
        fi
    else
        echo "⚠️  Redis not found (optional)"
    fi
    
    # Start the agent
    echo "🤖 Starting AI Social Media Agent..."
    python3 main.py
fi
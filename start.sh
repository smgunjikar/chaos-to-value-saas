#!/bin/bash

# AI Social Media Agent Startup Script
# This script sets up and starts the AI social media posting agent

set -e

echo "🤖 AI Social Media Agent Setup & Startup"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if .env file exists
check_env_file() {
    print_header "Checking environment configuration..."
    
    if [ ! -f ".env" ]; then
        print_warning ".env file not found!"
        print_status "Copying .env.example to .env..."
        cp .env.example .env
        print_error "Please edit .env file with your API keys and run this script again."
        echo ""
        echo "Required API keys:"
        echo "- OpenAI API Key (https://platform.openai.com/api-keys)"
        echo "- Anthropic API Key (https://console.anthropic.com/)"
        echo "- Twitter API Keys (https://developer.twitter.com/)"
        echo "- Facebook API Keys (https://developers.facebook.com/)"
        echo "- LinkedIn API Keys (https://www.linkedin.com/developers/)"
        echo ""
        exit 1
    else
        print_status ".env file found!"
    fi
}

# Check if Python is installed
check_python() {
    print_header "Checking Python installation..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed!"
        print_status "Please install Python 3.8+ and try again."
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2)
    print_status "Python $python_version found!"
}

# Install dependencies
install_dependencies() {
    print_header "Installing Python dependencies..."
    
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    print_status "Installing requirements..."
    pip install -r requirements.txt
    
    print_status "Dependencies installed successfully!"
}

# Setup database
setup_database() {
    print_header "Setting up database..."
    
    source venv/bin/activate
    python main.py --setup
    
    print_status "Database setup completed!"
}

# Function to start in different modes
start_cli() {
    print_header "Starting in CLI mode..."
    source venv/bin/activate
    python main.py --mode cli
}

start_daemon() {
    print_header "Starting in daemon mode..."
    source venv/bin/activate
    python main.py --mode daemon
}

start_web() {
    print_header "Starting web dashboard..."
    source venv/bin/activate
    python main.py --mode web
}

start_docker() {
    print_header "Starting with Docker..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed!"
        print_status "Please install Docker and try again."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed!"
        print_status "Please install Docker Compose and try again."
        exit 1
    fi
    
    print_status "Building and starting containers..."
    docker-compose up --build -d
    
    print_status "Containers started successfully!"
    print_status "Web dashboard: http://localhost:8000"
    print_status "API server: http://localhost:8080 (if enabled)"
    
    echo ""
    print_status "To view logs: docker-compose logs -f"
    print_status "To stop: docker-compose down"
}

generate_sample() {
    print_header "Generating sample content..."
    source venv/bin/activate
    python main.py --sample
}

# Main menu
show_menu() {
    echo ""
    echo "Choose startup mode:"
    echo "1) Interactive CLI mode (recommended for first-time setup)"
    echo "2) 24/7 daemon mode"
    echo "3) Web dashboard"
    echo "4) Docker deployment"
    echo "5) Generate sample content (test AI without posting)"
    echo "6) Exit"
    echo ""
}

# Main execution
main() {
    check_env_file
    check_python
    
    # Parse command line arguments
    if [ $# -eq 0 ]; then
        # No arguments, show interactive menu
        install_dependencies
        setup_database
        
        while true; do
            show_menu
            read -p "Enter your choice (1-6): " choice
            case $choice in
                1)
                    start_cli
                    break
                    ;;
                2)
                    start_daemon
                    break
                    ;;
                3)
                    start_web
                    break
                    ;;
                4)
                    start_docker
                    break
                    ;;
                5)
                    generate_sample
                    ;;
                6)
                    print_status "Goodbye!"
                    exit 0
                    ;;
                *)
                    print_error "Invalid choice. Please try again."
                    ;;
            esac
        done
    else
        # Handle command line arguments
        case $1 in
            cli)
                install_dependencies
                setup_database
                start_cli
                ;;
            daemon)
                install_dependencies
                setup_database
                start_daemon
                ;;
            web)
                install_dependencies
                setup_database
                start_web
                ;;
            docker)
                start_docker
                ;;
            sample)
                install_dependencies
                generate_sample
                ;;
            setup)
                install_dependencies
                setup_database
                print_status "Setup completed!"
                ;;
            *)
                echo "Usage: $0 [cli|daemon|web|docker|sample|setup]"
                echo ""
                echo "Modes:"
                echo "  cli     - Interactive CLI mode"
                echo "  daemon  - 24/7 background daemon"
                echo "  web     - Web dashboard"
                echo "  docker  - Docker deployment"
                echo "  sample  - Generate sample content"
                echo "  setup   - Setup only (no start)"
                echo ""
                echo "If no mode is specified, interactive menu will be shown."
                exit 1
                ;;
        esac
    fi
}

# Handle script interruption
cleanup() {
    echo ""
    print_status "Shutting down gracefully..."
    exit 0
}

trap cleanup SIGINT SIGTERM

# Run main function
main "$@"
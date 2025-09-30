#!/bin/bash

# AI Test Case Generator - Deployment Script
# Supports multiple deployment platforms

set -e

echo "🚀 AI Test Case Generator - Deployment Script"
echo "=============================================="

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found. Please run from project root."
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to deploy to Heroku
deploy_heroku() {
    echo "📦 Deploying to Heroku..."
    
    if ! command_exists heroku; then
        echo "❌ Heroku CLI not found. Please install from https://devcenter.heroku.com/articles/heroku-cli"
        exit 1
    fi
    
    cd api-server
    
    # Create Heroku app if it doesn't exist
    if ! heroku apps:info >/dev/null 2>&1; then
        echo "Creating new Heroku app..."
        heroku create
    fi
    
    # Set environment variables
    echo "Setting environment variables..."
    read -p "Enter OpenAI API Key: " OPENAI_KEY
    read -p "Enter Google API Key (optional): " GOOGLE_KEY
    read -p "Enter Anthropic API Key (optional): " ANTHROPIC_KEY
    
    heroku config:set OPENAI_API_KEY="$OPENAI_KEY"
    if [ ! -z "$GOOGLE_KEY" ]; then
        heroku config:set GOOGLE_API_KEY="$GOOGLE_KEY"
    fi
    if [ ! -z "$ANTHROPIC_KEY" ]; then
        heroku config:set ANTHROPIC_API_KEY="$ANTHROPIC_KEY"
    fi
    
    # Deploy
    echo "Deploying to Heroku..."
    git subtree push --prefix=api-server heroku main
    
    echo "✅ Deployed to Heroku!"
    echo "🌐 Your app is available at: https://$(heroku apps:info --json | jq -r '.app.web_url')"
}

# Function to deploy to Railway
deploy_railway() {
    echo "🚂 Deploying to Railway..."
    
    if ! command_exists railway; then
        echo "❌ Railway CLI not found. Please install from https://docs.railway.app/develop/cli"
        exit 1
    fi
    
    cd api-server
    
    # Login to Railway
    railway login
    
    # Initialize project
    railway init
    
    # Set environment variables
    echo "Setting environment variables..."
    read -p "Enter OpenAI API Key: " OPENAI_KEY
    read -p "Enter Google API Key (optional): " GOOGLE_KEY
    read -p "Enter Anthropic API Key (optional): " ANTHROPIC_KEY
    
    railway variables set OPENAI_API_KEY="$OPENAI_KEY"
    if [ ! -z "$GOOGLE_KEY" ]; then
        railway variables set GOOGLE_API_KEY="$GOOGLE_KEY"
    fi
    if [ ! -z "$ANTHROPIC_KEY" ]; then
        railway variables set ANTHROPIC_API_KEY="$ANTHROPIC_KEY"
    fi
    
    # Deploy
    railway up
    
    echo "✅ Deployed to Railway!"
}

# Function to deploy to Render
deploy_render() {
    echo "🎨 Deploying to Render..."
    echo "Please follow these steps:"
    echo "1. Go to https://render.com"
    echo "2. Connect your GitHub repository"
    echo "3. Create a new Web Service"
    echo "4. Select the 'api-server' folder"
    echo "5. Set environment variables:"
    echo "   - OPENAI_API_KEY"
    echo "   - GOOGLE_API_KEY (optional)"
    echo "   - ANTHROPIC_API_KEY (optional)"
    echo "6. Deploy!"
}

# Function to run locally
run_local() {
    echo "🏠 Running locally..."
    
    # Check Python
    if ! command_exists python3; then
        echo "❌ Python 3 not found. Please install Python 3.8+"
        exit 1
    fi
    
    # Install dependencies
    echo "Installing dependencies..."
    pip install -r requirements.txt
    cd api-server
    pip install -r requirements.txt
    cd ..
    
    # Set environment variables
    echo "Setting up environment variables..."
    read -p "Enter OpenAI API Key: " OPENAI_KEY
    read -p "Enter Google API Key (optional): " GOOGLE_KEY
    read -p "Enter Anthropic API Key (optional): " ANTHROPIC_KEY
    
    export OPENAI_API_KEY="$OPENAI_KEY"
    if [ ! -z "$GOOGLE_KEY" ]; then
        export GOOGLE_API_KEY="$GOOGLE_KEY"
    fi
    if [ ! -z "$ANTHROPIC_KEY" ]; then
        export ANTHROPIC_API_KEY="$ANTHROPIC_KEY"
    fi
    
    # Run the server
    echo "Starting local server..."
    cd api-server
    python app.py
}

# Function to setup GitHub Actions
setup_github_actions() {
    echo "⚙️ Setting up GitHub Actions..."
    echo "Please follow these steps:"
    echo "1. Go to your repository Settings → Secrets and variables → Actions"
    echo "2. Add the following secrets:"
    echo "   - OPENAI_API_KEY"
    echo "   - GOOGLE_API_KEY (optional)"
    echo "   - ANTHROPIC_API_KEY (optional)"
    echo "3. Go to Actions tab and run 'AI Test Case Generator' workflow"
}

# Main menu
echo ""
echo "Select deployment option:"
echo "1) Deploy to Heroku"
echo "2) Deploy to Railway"
echo "3) Deploy to Render (manual)"
echo "4) Run locally"
echo "5) Setup GitHub Actions"
echo "6) Exit"
echo ""

read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        deploy_heroku
        ;;
    2)
        deploy_railway
        ;;
    3)
        deploy_render
        ;;
    4)
        run_local
        ;;
    5)
        setup_github_actions
        ;;
    6)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "🎉 Deployment complete!"
echo "📚 For more information, see DEPLOYMENT.md"

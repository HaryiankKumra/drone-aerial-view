#!/bin/bash
# Campus Guardian Drone - Local Test Script

echo "🚁 Campus Guardian Drone - Starting..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Creating .env from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your Cloudinary credentials"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check if virtual environment exists
if [ ! -d .venv ]; then
    echo "❌ Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo "Installing dependencies..."
    .venv/bin/pip install -r requirements-deploy.txt
fi

# Kill any existing process on port 8080
echo "🧹 Cleaning up port 8080..."
lsof -ti:8080 | xargs kill -9 2>/dev/null || true

# Start the application
echo "🚀 Starting Campus Guardian Drone on http://localhost:8080"
echo "📊 CSV logs will be saved to: recordings/logs/"
echo "🎥 Videos will be saved to: recordings/events/"
echo "☁️  Cloudinary: ${CLOUDINARY_CLOUD_NAME}"
echo ""
echo "Press CTRL+C to stop"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

.venv/bin/python app.py

#!/bin/bash

# Portfolio Tracker Startup Script

echo "Starting Portfolio Tracker..."

# Navigate to the app directory
cd "/Users/sjonas/justin stock/Justin"

# Kill any existing processes on port 5001
echo "Checking for existing processes..."
lsof -ti:5001 | xargs kill -9 2>/dev/null || true

# Set environment variables
export FLASK_ENV="development"
export PORT="5001"

# Check if ANTHROPIC_API_KEY is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "WARNING: ANTHROPIC_API_KEY is not set. AI features will not work."
    echo "Please set it with: export ANTHROPIC_API_KEY='your-key-here'"
fi

# Start the application
echo "Starting Flask app on http://localhost:5001"
echo "Press Ctrl+C to stop the server"
echo ""

python3 app.py
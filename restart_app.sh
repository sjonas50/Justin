#!/bin/bash

echo "Stopping any existing Portfolio Tracker processes..."

# Kill any Python processes running app.py
pkill -f "python.*app.py" 2>/dev/null || true

# Kill anything on port 5001
lsof -ti:5001 | xargs kill -9 2>/dev/null || true

echo "Waiting for ports to be released..."
sleep 2

echo "Starting Portfolio Tracker..."
./start_app.sh
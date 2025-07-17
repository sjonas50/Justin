#!/usr/bin/env python3
"""Simple runner script to ensure correct Python environment"""
import os
import sys

# Set environment variables
os.environ['ANTHROPIC_API_KEY'] = os.environ.get('ANTHROPIC_API_KEY', '')
os.environ['FLASK_ENV'] = 'development'
os.environ['PORT'] = '5001'

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Import and run the app
    from app import app
    print("Starting Portfolio Tracker on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=False)
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("\nPlease install required packages:")
    print("pip install Flask anthropic yfinance pandas numpy")
except Exception as e:
    print(f"Error starting app: {e}")
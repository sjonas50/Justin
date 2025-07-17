# Portfolio Tracker - Enhanced Version

A comprehensive stock portfolio tracking application with AI-powered investment suggestions using Claude 3.5 Sonnet.

## Key Improvements Made

### 1. **AI Integration Upgrade**
- ✅ Updated from deprecated Claude 2.1 to Claude 3.5 Sonnet
- ✅ Migrated from old completions API to modern messages API
- ✅ Enhanced prompts for better, more personalized suggestions
- ✅ Added comprehensive error handling for API calls

### 2. **Security Enhancements**
- ✅ Fixed SQL injection vulnerabilities with parameterized queries
- ✅ Added comprehensive input validation for all user inputs
- ✅ Created validation utilities for tickers, quantities, and text
- ✅ Removed debug mode in production
- ✅ Added proper error handling and logging

### 3. **Architecture Improvements**
- ✅ Added configuration management system
- ✅ Implemented proper error handling throughout
- ✅ Created error pages (404, 500)
- ✅ Added logging with rotation
- ✅ Improved code organization

### 4. **Enhanced Portfolio Features**
- ✅ Real-time portfolio value calculations
- ✅ Daily gain/loss tracking
- ✅ Dividend income calculations
- ✅ Portfolio diversification analysis
- ✅ Company name display
- ✅ 52-week high/low tracking
- ✅ Performance metrics

### 5. **UI/UX Improvements**
- ✅ Modern, responsive design with gradient themes
- ✅ Interactive portfolio dashboard
- ✅ Real-time diversification chart
- ✅ Modal dialogs for stock operations
- ✅ Flash messages for user feedback
- ✅ Loading states and animations
- ✅ Mobile-friendly responsive design

### 6. **Performance Optimizations**
- ✅ Implemented caching system for stock prices (5-min TTL)
- ✅ Batch API calls for multiple stocks
- ✅ Reduced redundant API requests
- ✅ Optimized database queries

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone git@github.com:sjonas50/Justin.git
   cd Justin
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   ```bash
   export ANTHROPIC_API_KEY="your-api-key-here"
   export FLASK_ENV="production"  # or "development" for dev mode
   ```

4. **Initialize databases**
   ```bash
   python create_user_profiles_table.py
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

## Features

- **Portfolio Management**: Add/remove stocks, track quantities
- **Real-time Data**: Live stock prices and daily changes
- **AI Suggestions**: Personalized investment advice using Claude 3.5
- **Goal Tracking**: Set and monitor financial targets
- **Performance Analytics**: Portfolio value, gains/losses, dividends
- **Interactive Chat**: Ask questions about your portfolio
- **Visualizations**: Portfolio diversification charts

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite
- **AI**: Anthropic Claude 3.5 Sonnet
- **Market Data**: Yahoo Finance (yfinance)
- **Frontend**: HTML, CSS, JavaScript, Chart.js
- **Caching**: In-memory cache with TTL

## Security Notes

- Input validation on all user inputs
- SQL injection protection
- XSS prevention
- Secure configuration management
- Production-ready error handling

## Future Enhancements

- Historical performance tracking
- Export functionality (CSV/PDF)
- More advanced analytics
- Email notifications
- Integration with brokerage APIs
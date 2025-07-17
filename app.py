from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from portfolio_tracker import Portfolio
from ml_analysis import generate_suggestions, generate_chat_response
from database import save_user_profile, retrieve_user_profile
from utils import validate_ticker, validate_quantity
from config import get_config
from cache import get_stock_info_cached
import yfinance as yf
import logging
from logging.handlers import RotatingFileHandler
import os
from functools import wraps

# Get configuration
config = get_config()

app = Flask(__name__)
app.config.from_object(config)

# Set up logging
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/portfolio_tracker.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Portfolio Tracker startup')

def handle_errors(f):
    """Decorator to handle errors in routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            app.logger.error(f'Validation error in {f.__name__}: {str(e)}')
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            app.logger.error(f'Error in {f.__name__}: {str(e)}')
            return jsonify({'error': 'An unexpected error occurred'}), 500
    return decorated_function

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'message': 'Portfolio Tracker is running'})

@app.route('/portfolio', methods=['GET', 'POST'])
@handle_errors
def portfolio():
    if request.method == 'POST':
        try:
            # Retrieve user information from the form
            name = request.form['name']
            age = int(request.form['age'])
            investment_amount = float(request.form['investment_amount'])
            goal1 = request.form['goal1']
            goal2 = request.form['goal2']
            goal3 = request.form['goal3']
            target_age = int(request.form['target_age'])
            target_portfolio_value = float(request.form['target_portfolio_value'])
            target_dividend_income = float(request.form['target_dividend_income'])
            
            # Save the user profile data to the database
            save_user_profile(name, age, investment_amount, goal1, goal2, goal3,
                              target_age, target_portfolio_value, target_dividend_income)
            
            # Create an instance of the Portfolio class
            portfolio = Portfolio('stock_database.db')
            
            # Retrieve the user's portfolio data
            portfolio_data = portfolio.get_portfolio_data()
            portfolio_summary = portfolio.get_portfolio_summary()

            labels = [stock['ticker'] for stock in portfolio_data]
            quantities = [stock['quantity'] for stock in portfolio_data]
            
            return render_template('portfolio.html', 
                                   portfolio_data=portfolio_data, 
                                   portfolio_summary=portfolio_summary,
                                   labels=labels, 
                                   quantities=quantities, 
                                   name=name, 
                                   age=age,
                                   investment_amount=investment_amount, 
                                   goals=[goal1, goal2, goal3],
                                   target_age=target_age, 
                                   target_portfolio_value=target_portfolio_value,
                                   target_dividend_income=target_dividend_income)
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('home'))
        except Exception as e:
            app.logger.error(f'Error in portfolio POST: {str(e)}')
            flash('An error occurred while saving your profile. Please try again.', 'error')
            return redirect(url_for('home'))
    else:
        # Create an instance of the Portfolio class
        portfolio = Portfolio('stock_database.db')
        
        # Retrieve the user's portfolio data
        portfolio_data = portfolio.get_portfolio_data()
        portfolio_summary = portfolio.get_portfolio_summary()
        
        # Retrieve the user's profile data from the database
        user_profile = retrieve_user_profile()
        
        if user_profile:
            name = user_profile['name']
            age = user_profile['age']
            investment_amount = user_profile['investment_amount']
            goal1 = user_profile['goal1']
            goal2 = user_profile['goal2']
            goal3 = user_profile['goal3']
            target_age = user_profile['target_age']
            target_portfolio_value = user_profile['target_portfolio_value']
            target_dividend_income = user_profile['target_dividend_income']
        else:
            name = ''
            age = 0
            investment_amount = 0
            goal1 = ''
            goal2 = ''
            goal3 = ''
            target_age = 0
            target_portfolio_value = 0
            target_dividend_income = 0
        
        return render_template('portfolio.html', 
                               portfolio_data=portfolio_data, 
                               portfolio_summary=portfolio_summary,
                               name=name, 
                               age=age,
                               investment_amount=investment_amount, 
                               goals=[goal1, goal2, goal3],
                               target_age=target_age, 
                               target_portfolio_value=target_portfolio_value,
                               target_dividend_income=target_dividend_income)
    
@app.route('/add_stock', methods=['POST'])
@handle_errors
def add_stock():
    try:
        ticker = request.form['ticker']
        quantity = request.form['quantity']
        
        # Retrieve user information and target goals from the form
        name = request.form.get('name', '')
        age = int(request.form.get('age', 0))
        investment_amount = float(request.form.get('investment_amount', 0))
        goal1 = request.form.get('goal1', '')
        goal2 = request.form.get('goal2', '')
        goal3 = request.form.get('goal3', '')
        target_age = int(request.form.get('target_age', 0))
        target_portfolio_value = float(request.form.get('target_portfolio_value', 0))
        target_dividend_income = float(request.form.get('target_dividend_income', 0))
        
        # Create an instance of the Portfolio class
        portfolio = Portfolio('stock_database.db')
        
        # Add the stock to the user's portfolio (validation happens inside)
        portfolio.add_stock(ticker, quantity)
        
        # Retrieve the updated portfolio data
        portfolio_data = portfolio.get_portfolio_data()
        
        flash(f'Successfully added {quantity} shares of {ticker.upper()}', 'success')
        
        return render_template('portfolio.html', portfolio_data=portfolio_data, name=name, age=age,
                               investment_amount=investment_amount, goals=[goal1, goal2, goal3],
                               target_age=target_age, target_portfolio_value=target_portfolio_value,
                               target_dividend_income=target_dividend_income)
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('portfolio'))
    except Exception as e:
        app.logger.error(f'Error adding stock: {str(e)}')
        flash('Error adding stock. Please check the ticker symbol and try again.', 'error')
        return redirect(url_for('portfolio'))

@app.route('/remove_stock', methods=['POST'])
def remove_stock():
    ticker = request.form['ticker']
    
    # Retrieve user information and target goals from the form
    name = request.form['name']
    age = int(request.form['age'])
    investment_amount = float(request.form['investment_amount'])
    goal1 = request.form['goal1']
    goal2 = request.form['goal2']
    goal3 = request.form['goal3']
    target_age = int(request.form['target_age'])
    target_portfolio_value = float(request.form['target_portfolio_value'])
    target_dividend_income = float(request.form['target_dividend_income'])
    
    # Create an instance of the Portfolio class
    portfolio = Portfolio('stock_database.db')
    
    # Remove the stock from the user's portfolio
    portfolio.remove_stock(ticker)
    
    # Retrieve the updated portfolio data
    portfolio_data = portfolio.get_portfolio_data()
    
    return render_template('portfolio.html', portfolio_data=portfolio_data, name=name, age=age,
                           investment_amount=investment_amount, goals=[goal1, goal2, goal3],
                           target_age=target_age, target_portfolio_value=target_portfolio_value,
                           target_dividend_income=target_dividend_income)

@app.route('/stock_quote', methods=['POST'])
@handle_errors
def stock_quote():
    ticker = request.form['ticker']
    
    # Validate ticker
    valid, ticker = validate_ticker(ticker)
    if not valid:
        return jsonify({'error': ticker}), 400
    
    # Retrieve stock information with caching
    info = get_stock_info_cached(ticker)
    
    # Extract relevant information
    stock_info = {
        'ticker': ticker,
        'price': info['currentPrice'],
        'previous_close': info['previousClose'],
        'open_price': info['open'],
        'bid': info['bid'],
        'ask': info['ask'],
        'day_range': f"{info['dayLow']} - {info['dayHigh']}",
        'week_range': f"{info['fiftyTwoWeekLow']} - {info['fiftyTwoWeekHigh']}",
        'volume': info['volume'],
        'avg_volume': info['averageVolume'],
        'market_cap': info['marketCap'],
        'beta': info['beta'],
        'pe_ratio': info['trailingPE'],
        'eps': info['trailingEps'],
        'earnings_date': info.get('earningsDate', 'N/A'),
        'dividend_rate': info.get('dividendRate', 'N/A'),
        'forward_dividend': info.get('dividendRate', 'N/A'),
        'ex_dividend_date': info.get('exDividendDate', 'N/A'),
        'target_est': info.get('targetMeanPrice', 'N/A')
    }
    
    return jsonify(stock_info=stock_info)

@app.route('/generate_suggestions', methods=['POST'])
def generate_suggestions_route():
    # Retrieve user information and investment goals from the form
    name = request.form.get('name', '')
    age = request.form.get('age', '0')
    investment_amount = request.form.get('investment_amount', '0')
    goals = request.form.getlist('goals[]')
    target_age = request.form.get('target_age', '0')
    target_portfolio_value = request.form.get('target_portfolio_value', '0')
    target_dividend_income = request.form.get('target_dividend_income', '0')
    
    # Convert form fields to appropriate data types
    age = int(age) if age.isdigit() else 0
    investment_amount = float(investment_amount) if investment_amount else 0
    target_age = int(target_age) if target_age.isdigit() else 0
    target_portfolio_value = float(target_portfolio_value) if target_portfolio_value else 0
    target_dividend_income = float(target_dividend_income) if target_dividend_income else 0
    
    # Create an instance of the Portfolio class
    portfolio = Portfolio('stock_database.db')
    
    # Retrieve the user's portfolio data
    portfolio_data = portfolio.get_portfolio_data()
    
    # Generate investment suggestions using the Claude API
    suggestions = generate_suggestions(name, age, investment_amount, portfolio_data, goals,
                                       target_age, target_portfolio_value, target_dividend_income)
    
    return render_template('suggestions.html', suggestions=suggestions)

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form['user_input']
    
    # Retrieve the user's portfolio data
    portfolio = Portfolio('stock_database.db')
    portfolio_data = portfolio.get_portfolio_data()
    
    # Generate a response using the Claude API
    response = generate_chat_response(user_input, portfolio_data)
    
    return response

@app.route('/calculate_portfolio_value', methods=['GET'])
def calculate_portfolio_value():
    # Create an instance of the Portfolio class
    portfolio = Portfolio('stock_database.db')
    
    # Calculate the portfolio value
    portfolio_value = portfolio.portfolio_value
    
    return jsonify({'portfolio_value': portfolio_value})

@app.route('/suggestions', methods=['GET', 'POST'])
def suggestions():
    if request.method == 'POST':
        # Retrieve user information and investment goals from the form
        name = request.form['name']
        age = int(request.form['age'])
        investment_amount = float(request.form['investment_amount'])
        goal1 = request.form['goal1']
        goal2 = request.form['goal2']
        goal3 = request.form['goal3']
        
        # Create an instance of the Portfolio class
        portfolio = Portfolio('stock_database.db')
        
        # Retrieve the user's portfolio data
        portfolio_data = portfolio.get_portfolio_data()
        
        # Generate investment suggestions using the Claude API
        suggestions = generate_suggestions(name, age, investment_amount, portfolio_data, [goal1, goal2, goal3])
        
        return render_template('suggestions.html', suggestions=suggestions)
    
    return redirect(url_for('home'))

@app.errorhandler(404)
def not_found_error(error):
    app.logger.error(f'404 error: {error}')
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'500 error: {error}')
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Run in production mode by default
    # Set FLASK_ENV=development for development mode
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
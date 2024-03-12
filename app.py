from flask import Flask, render_template, request, redirect, url_for
from portfolio_tracker import Portfolio
from ml_analysis import generate_suggestions
from ml_analysis import generate_chat_response
from database import save_user_profile
from database import retrieve_user_profile
from flask import jsonify
import yfinance as yf


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/portfolio', methods=['GET', 'POST'])
def portfolio():
    if request.method == 'POST':
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

        labels = [stock['ticker'] for stock in portfolio_data]
        quantities = [stock['quantity'] for stock in portfolio_data]
        
        return render_template('portfolio.html', portfolio_data=portfolio_data, labels=labels, quantities=quantities, name=name, age=age,
                               investment_amount=investment_amount, goals=[goal1, goal2, goal3],
                               target_age=target_age, target_portfolio_value=target_portfolio_value,
                               target_dividend_income=target_dividend_income)
    else:
        # Create an instance of the Portfolio class
        portfolio = Portfolio('stock_database.db')
        
        # Retrieve the user's portfolio data
        portfolio_data = portfolio.get_portfolio_data()
        
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
        
        return render_template('portfolio.html', portfolio_data=portfolio_data, name=name, age=age,
                               investment_amount=investment_amount, goals=[goal1, goal2, goal3],
                               target_age=target_age, target_portfolio_value=target_portfolio_value,
                               target_dividend_income=target_dividend_income)
    
@app.route('/add_stock', methods=['POST'])
def add_stock():
    ticker = request.form['ticker']
    quantity = int(request.form['quantity'])
    
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
    
    # Add the stock to the user's portfolio
    portfolio.add_stock(ticker, quantity)
    
    # Retrieve the updated portfolio data
    portfolio_data = portfolio.get_portfolio_data()
    
    return render_template('portfolio.html', portfolio_data=portfolio_data, name=name, age=age,
                           investment_amount=investment_amount, goals=[goal1, goal2, goal3],
                           target_age=target_age, target_portfolio_value=target_portfolio_value,
                           target_dividend_income=target_dividend_income)

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
def stock_quote():
    ticker = request.form['ticker']
    
    # Retrieve stock information from Yahoo Finance
    stock = yf.Ticker(ticker)
    info = stock.info
    
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

if __name__ == '__main__':
    app.run(debug=True)
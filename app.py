from flask import Flask, render_template, request, redirect, url_for
from portfolio_tracker import Portfolio
from ml_analysis import generate_suggestions
from ml_analysis import generate_chat_response

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/portfolio', methods=['GET', 'POST'])
def portfolio():
    if request.method == 'POST':
        # Retrieve user information and investment goals from the form
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
        
        # Retrieve the user's portfolio data
        portfolio_data = portfolio.get_portfolio_data()
        
        return render_template('portfolio.html', portfolio_data=portfolio_data, name=name, age=age,
                               investment_amount=investment_amount, goals=[goal1, goal2, goal3],
                               target_age=target_age, target_portfolio_value=target_portfolio_value,
                               target_dividend_income=target_dividend_income)
    
    return redirect(url_for('home'))

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

@app.route('/generate_suggestions', methods=['POST'])
def generate_suggestions_route():
    # Retrieve user information and investment goals from the form
    name = request.form['name']
    age = int(request.form['age'])
    investment_amount = float(request.form['investment_amount'])
    goals = request.form.getlist('goals[]')
    target_age = int(request.form['target_age'])
    target_portfolio_value = float(request.form['target_portfolio_value'])
    target_dividend_income = float(request.form['target_dividend_income'])
    
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
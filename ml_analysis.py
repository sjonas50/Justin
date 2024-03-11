import sqlite3
import pandas as pd
from data_preprocessing import create_database_connection
import anthropic
import os
import yfinance as yf
from portfolio_tracker import Portfolio

def preprocess_data(db_name):
    # Retrieve the preprocessed stock data from the database
    conn = create_database_connection(db_name)
    query = "SELECT * FROM preprocessed_stock_data"
    data = pd.read_sql_query(query, conn)
    conn.close()
    return data

def generate_suggestions(name, age, investment_amount, portfolio_data, goals,
                         target_age, target_portfolio_value, target_dividend_income):
    # Convert portfolio data to a formatted string
    portfolio_summary = ""
    for stock in portfolio_data:
        portfolio_summary += f"Ticker: {stock['ticker']}, Quantity: {stock['quantity']}\n"
    
    # Convert goals to a formatted string
    goals_summary = "\n".join(goals)
    
    # Prepare the prompt for the Claude API
    prompt = f"""User Information:
Name: {name}
Age: {age}
Investment Amount: {investment_amount}

Portfolio Data:
"""
    for stock in portfolio_data:
        prompt += f"Ticker: {stock['ticker']}, Quantity: {stock['quantity']}, Current Price: {stock['current_price']}\n"
    
    prompt += f"""
Investment Goals:
{goals_summary}

Target Goals:
Target Age: {target_age}
Target Portfolio Value: {target_portfolio_value}
Target Dividend Income: {target_dividend_income}

Please provide investment suggestions based on the given user information, portfolio data (including current stock prices), goals, and target goals.  Always provide investment advice based upon the portfolio data and goals and be thorough and specific, and call the user by name "Justin".
"""
    
    # Make a request to the Claude API
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    client = anthropic.Client(api_key=api_key)
    response = client.completions.create(
        prompt=f"{anthropic.HUMAN_PROMPT} {prompt} {anthropic.AI_PROMPT}",
        stop_sequences=[anthropic.HUMAN_PROMPT],
        model="claude-2.1",
        max_tokens_to_sample=1000,
        temperature=0.7,
    )
    
    # Extract the generated suggestions from the API response
    suggestions = response.completion.strip().split("\n")
    
    return suggestions

def main():
    db_name = 'stock_database.db'
    
    # Preprocess the stock data
    data = preprocess_data(db_name)
    
    # Retrieve the user's portfolio data and investment goals
    portfolio_data = retrieve_portfolio_data(db_name)
    goals = retrieve_investment_goals(db_name)
    
    # Generate investment suggestions using the Claude API
    suggestions = generate_suggestions(portfolio_data, goals)
    
    # Print or return the suggestions
    print("Investment Suggestions:")
    for suggestion in suggestions:
        print(suggestion)

def retrieve_portfolio_data(db_name):
    conn = create_database_connection(db_name)
    query = "SELECT * FROM portfolio"
    portfolio_data = pd.read_sql_query(query, conn)
    conn.close()
    return portfolio_data

def retrieve_investment_goals(db_name):
    # Implement your own logic to retrieve the user's investment goals from the database or any other source
    goals = [
        "Achieve long-term capital growth",
        "Generate steady income through dividends"
    ]
    return goals

def generate_chat_response(user_input, portfolio_data):
    # Convert portfolio data to a formatted string
    portfolio_summary = ""
    for stock in portfolio_data:
        portfolio_summary += f"Ticker: {stock['ticker']}, Quantity: {stock['quantity']}\n"

    # Create an instance of the Portfolio class
    portfolio = Portfolio('stock_database.db')

    # Retrieve the user's portfolio data with live stock prices
    portfolio_data_with_live_prices = portfolio.get_portfolio_data()

    # Convert portfolio data with live prices to a formatted string
    portfolio_summary_with_live_prices = ""
    for stock in portfolio_data_with_live_prices:
        portfolio_summary_with_live_prices += f"Ticker: {stock['ticker']}, Quantity: {stock['quantity']}, Current Price: {stock['current_price']}\n"

    # Prepare the prompt for the Claude API
    prompt = f"""
User's Portfolio:
{portfolio_summary_with_live_prices}

User's Question: {user_input}

Please provide a response to the user's question based on their portfolio data with live stock prices and their goals. The user's name is Justin, please use their name as well.
"""

    
    # Make a request to the Claude API
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    client = anthropic.Client(api_key=api_key)
    response = client.completions.create(
        prompt=f"{anthropic.HUMAN_PROMPT} {prompt} {anthropic.AI_PROMPT}",
        stop_sequences=[anthropic.HUMAN_PROMPT],
        model="claude-2.1",
        max_tokens_to_sample=1000,
        temperature=0.7,
    )
    
    # Extract the generated response from the API response
    chat_response = response.completion.strip()
    
    return chat_response

if __name__ == '__main__':
    main()
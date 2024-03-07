import sqlite3
import pandas as pd
from data_preprocessing import create_database_connection
import anthropic

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
{portfolio_summary}

Investment Goals:
{goals_summary}

Target Goals:
Target Age: {target_age}
Target Portfolio Value: {target_portfolio_value}
Target Dividend Income: {target_dividend_income}

Please provide investment suggestions based on the given user information, portfolio data, goals, and target goals, and call the user by name "Justin".
"""
    
    # Make a request to the Claude API
    client = anthropic.Client()
    response = client.completions.create(
        prompt=f"{anthropic.HUMAN_PROMPT} {prompt} {anthropic.AI_PROMPT}",
        stop_sequences=[anthropic.HUMAN_PROMPT],
        model="claude-v1",
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
    
    # Prepare the prompt for the Claude API
    prompt = f"""
User's Portfolio:
{portfolio_summary}

User's Question: {user_input}

Please provide a response to the user's question based on their portfolio data.  The users name is Justin, please use his name as well.
"""
    
    # Make a request to the Claude API
    client = anthropic.Client()
    response = client.completions.create(
        prompt=f"{anthropic.HUMAN_PROMPT} {prompt} {anthropic.AI_PROMPT}",
        stop_sequences=[anthropic.HUMAN_PROMPT],
        model="claude-v1",
        max_tokens_to_sample=1000,
        temperature=0.7,
    )
    
    # Extract the generated response from the API response
    chat_response = response.completion.strip()
    
    return chat_response

if __name__ == '__main__':
    main()
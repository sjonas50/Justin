import sqlite3
import pandas as pd
from data_preprocessing import create_database_connection
import anthropic
import os
import yfinance as yf
from portfolio_tracker import Portfolio
from database import retrieve_user_profile

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
    total_portfolio_value = 0
    for stock in portfolio_data:
        stock_value = stock['quantity'] * stock['current_price']
        total_portfolio_value += stock_value
        portfolio_summary += f"- {stock['ticker']}: {stock['quantity']} shares @ ${stock['current_price']:.2f} = ${stock_value:,.2f}\n"
    
    # Convert goals to a formatted string
    goals_summary = "\n".join([f"- {goal}" for goal in goals if goal])
    
    # Calculate years to target and required growth
    years_to_target = target_age - age if target_age > age else 0
    
    # Prepare the prompt for the Claude API
    prompt = f"""You are an expert financial advisor helping {name} with their investment portfolio.

Current Situation:
- Name: {name}
- Current Age: {age}
- Investment Amount Available: ${investment_amount:,.2f}
- Current Portfolio Value: ${total_portfolio_value:,.2f}

Current Portfolio Holdings:
{portfolio_summary}

Investment Goals:
{goals_summary}

Target Goals:
- Target Age: {target_age} ({years_to_target} years from now)
- Target Portfolio Value: ${target_portfolio_value:,.2f}
- Target Annual Dividend Income: ${target_dividend_income:,.2f}

Please provide specific, actionable investment suggestions including:
1. Analysis of the current portfolio (diversification, risk level, dividend yield)
2. Specific stocks to consider adding or increasing positions
3. Any stocks to consider reducing or removing
4. Allocation recommendations based on their goals
5. Timeline and milestones to reach their targets
6. Risk considerations and mitigation strategies

Be thorough, specific, and personalized to {name}'s situation."""
    
    try:
        # Make a request to the Claude API using the new SDK
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            return ["Error: ANTHROPIC_API_KEY environment variable not set. Please set it to use AI suggestions."]
        
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            temperature=0.7,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        # Extract the generated suggestions from the API response
        suggestions = response.content[0].text.strip().split("\n")
        
        return suggestions
    except Exception as e:
        return [f"Error generating suggestions: {str(e)}"]

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
    # Create an instance of the Portfolio class
    portfolio = Portfolio('stock_database.db')

    # Retrieve the user's portfolio data with live stock prices
    portfolio_data_with_live_prices = portfolio.get_portfolio_data()

    # Convert portfolio data with live prices to a formatted string
    portfolio_summary = ""
    total_value = 0
    total_daily_change = 0
    
    for stock in portfolio_data_with_live_prices:
        stock_value = stock['quantity'] * stock['current_price']
        total_value += stock_value
        
        # Get additional stock info for better responses
        try:
            ticker_info = yf.Ticker(stock['ticker']).info
            daily_change = ticker_info.get('regularMarketChange', 0)
            daily_change_percent = ticker_info.get('regularMarketChangePercent', 0)
            total_daily_change += daily_change * stock['quantity']
            
            portfolio_summary += f"- {stock['ticker']}: {stock['quantity']} shares @ ${stock['current_price']:.2f} (${daily_change:+.2f}, {daily_change_percent:+.2f}%) = ${stock_value:,.2f}\n"
        except:
            portfolio_summary += f"- {stock['ticker']}: {stock['quantity']} shares @ ${stock['current_price']:.2f} = ${stock_value:,.2f}\n"

    # Retrieve user profile for context
    user_profile = retrieve_user_profile()
    name = user_profile['name'] if user_profile else "Justin"
    
    # Prepare the prompt for the Claude API
    prompt = f"""You are a knowledgeable and friendly financial advisor assistant helping {name} with their investment portfolio.

Current Portfolio Summary:
- Total Portfolio Value: ${total_value:,.2f}
- Today's Change: ${total_daily_change:+,.2f}

Holdings:
{portfolio_summary}

User's Question: {user_input}

Please provide a helpful, specific response to {name}'s question. Consider their portfolio composition, current market conditions, and investment best practices. Be conversational but professional."""

    try:
        # Make a request to the Claude API using the new SDK
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            return "Error: ANTHROPIC_API_KEY environment variable not set. Please set it to use the chat feature."
        
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            temperature=0.7,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        # Extract the generated response from the API response
        chat_response = response.content[0].text.strip()
        
        return chat_response
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}. Please try again later."

if __name__ == '__main__':
    main()
import sqlite3
import pandas as pd
from data_retrieval import get_stock_data
from data_preprocessing import create_database_connection
import yfinance as yf

class Portfolio:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = create_database_connection(db_name)
        self.stocks = self._load_portfolio()
        self.portfolio_value = 0
        self.update_portfolio_value()

    def add_stock(self, ticker, quantity):
    # Validate the stock ticker using yfinance
        try:
            stock_info = yf.Ticker(ticker).info
            if 'currentPrice' not in stock_info or stock_info['currentPrice'] is None:
                print(f"Invalid ticker or missing market price: {ticker}")
                return
        except Exception as e:
            print(f"Error validating ticker {ticker}: {str(e)}")
            return
        
        # Check if the stock is already in the portfolio
        for stock in self.stocks:
            if stock['ticker'] == ticker:
                # Update the quantity if the stock is already in the portfolio
                stock['quantity'] += quantity
                self._save_portfolio()
                self.update_portfolio_value()
                return
        
        # Add the stock to the portfolio if it's not already present
        stock = {'ticker': ticker, 'quantity': quantity}
        self.stocks.append(stock)
        self._save_portfolio()
        self.update_portfolio_value()
        
        print(f"Added stock: {ticker}, Quantity: {quantity}")

    def remove_stock(self, ticker):
        self.stocks = [stock for stock in self.stocks if stock['ticker'] != ticker]
        self._save_portfolio()
        self.update_portfolio_value()

    def get_portfolio_data(self):
        portfolio_data = []
        for stock in self.stocks:
            ticker = stock['ticker']
            quantity = stock['quantity']

            # Fetch live stock price using yfinance
            try:
                stock_info = yf.Ticker(ticker).info
                current_price = stock_info.get('currentPrice', 0)  # Use get() with default value of 0
            except Exception as e:
                print(f"Error fetching stock data for {ticker}: {str(e)}")
                current_price = 0  # Assign a default value of 0 in case of an error

            stock_data = {
                'ticker': ticker,
                'quantity': quantity,
                'current_price': current_price
            }
            portfolio_data.append(stock_data)

        print(f"Portfolio Data: {portfolio_data}")

        return portfolio_data

    def calculate_returns(self):
        total_return = 0
        for stock in self.stocks:
            ticker = stock['ticker']
            quantity = stock['quantity']
            
            # Fetch historical stock data using yfinance
            stock_data = yf.download(ticker, start='2022-01-01', end='2023-06-08')
            
            if not stock_data.empty:
                initial_price = stock_data['Close'].iloc[0]
                current_price = stock_data['Close'].iloc[-1]
                stock_return = (current_price - initial_price) * quantity
                total_return += stock_return
        
        return total_return

    def calculate_dividend_yield(self):
        total_dividend_yield = 0
        for stock in self.stocks:
            ticker = stock['ticker']
            quantity = stock['quantity']
            
            # Fetch dividend data using yfinance
            stock_info = yf.Ticker(ticker).info
            dividend_yield = stock_info.get('trailingAnnualDividendYield', 0)

            
            if dividend_yield is not None:
                total_dividend_yield += dividend_yield * quantity
        
        return total_dividend_yield

    def update_stock_quantity(self, ticker, new_quantity):
        for stock in self.stocks:
            if stock['ticker'] == ticker:
                stock['quantity'] = new_quantity
                break
        self._save_portfolio()
        self.update_portfolio_value()

    def update_portfolio_value(self):
        self.portfolio_value = self.calculate_portfolio_value()

    def calculate_portfolio_value(self):
        portfolio_value = 0
        for stock in self.stocks:
            ticker = stock['ticker']
            quantity = stock['quantity']
        
            try:
                # Fetch live stock price using yfinance
                stock_info = yf.Ticker(ticker).info
                current_price = stock_info.get('currentPrice', 0)
            
                print(f"Ticker: {ticker}, Quantity: {quantity}, Current Price: {current_price}")
            
                stock_value = current_price * quantity
                portfolio_value += stock_value
            except Exception as e:
                print(f"Error fetching stock data for {ticker}: {str(e)}")
    
        print(f"Portfolio Value: {portfolio_value}")
        return portfolio_value

    def generate_performance_report(self):
        # Implement the logic to generate a performance report
        # You can use the calculated metrics and historical data
        pass

    def _load_portfolio(self):
        # Load the portfolio from the database
        query = "SELECT * FROM portfolio"
        portfolio_data = pd.read_sql_query(query, self.conn)
        stocks = []
        for _, row in portfolio_data.iterrows():
            stock = {'ticker': row['ticker'], 'quantity': row['quantity']}
            stocks.append(stock)
        return stocks

    def _save_portfolio(self):
        # Save the updated portfolio to the database
        conn = create_database_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM portfolio")
        for stock in self.stocks:
            ticker = stock['ticker']
            quantity = stock['quantity']
            cursor.execute("INSERT INTO portfolio (ticker, quantity) VALUES (?, ?)", (ticker, quantity))
        conn.commit()
        conn.close()

    def _get_stock_data(self, ticker):
        # Retrieve the stock data from the database
        query = f"SELECT * FROM preprocessed_stock_data WHERE ticker = '{ticker}'"
        stock_data = pd.read_sql_query(query, self.conn)
        return stock_data

def create_portfolio_table(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS portfolio (
            ticker TEXT,
            quantity INTEGER
        )
    """)
    conn.commit()
    conn.close()

def main():
    db_name = 'stock_database.db'

    # Create the portfolio table if it doesn't exist
    create_portfolio_table(db_name)

    portfolio = Portfolio(db_name)

    # Example usage
    portfolio.add_stock('AAPL', 10)
    portfolio.add_stock('GOOGL', 5)
    portfolio.update_stock_quantity('AAPL', 15)
    portfolio.remove_stock('GOOGL')

    portfolio_data = portfolio.get_portfolio_data()
    for stock in portfolio_data:
        print(f"Ticker: {stock['ticker']}, Quantity: {stock['quantity']}, Current Price: {stock['current_price']}")

    portfolio_value = portfolio.calculate_portfolio_value()
    print(f"Portfolio Value: ${portfolio_value:.2f}")

    # Calculate returns and dividend yield
    returns = portfolio.calculate_returns()
    dividend_yield = portfolio.calculate_dividend_yield()
    print(f"Total Returns: ${returns:.2f}")
    print(f"Dividend Yield: {dividend_yield:.2%}")

    # Generate performance report
    portfolio.generate_performance_report()

if __name__ == '__main__':
    main()
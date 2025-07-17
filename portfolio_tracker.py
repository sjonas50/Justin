import sqlite3
import pandas as pd
from data_retrieval import get_stock_data
from data_preprocessing import create_database_connection
import yfinance as yf
from cache import get_stock_info_cached, get_multiple_stocks_cached

class Portfolio:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = create_database_connection(db_name)
        self.stocks = self._load_portfolio()
        self.portfolio_value = 0
        self.update_portfolio_value()

    def add_stock(self, ticker, quantity):
        from utils import validate_ticker, validate_quantity
        
        # Validate inputs
        valid, ticker = validate_ticker(ticker)
        if not valid:
            raise ValueError(ticker)
        
        valid, quantity = validate_quantity(quantity)
        if not valid:
            raise ValueError(quantity)
        
        # Validate the stock ticker using cached info
        try:
            stock_info = get_stock_info_cached(ticker)
            if 'currentPrice' not in stock_info or stock_info['currentPrice'] is None:
                raise ValueError(f"Invalid ticker or missing market price: {ticker}")
        except Exception as e:
            raise ValueError(f"Error validating ticker {ticker}: {str(e)}")
        
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
        from utils import validate_ticker
        
        # Validate input
        valid, ticker = validate_ticker(ticker)
        if not valid:
            raise ValueError(ticker)
        
        self.stocks = [stock for stock in self.stocks if stock['ticker'] != ticker]
        self._save_portfolio()
        self.update_portfolio_value()

    def get_portfolio_data(self):
        portfolio_data = []
        
        # Get all tickers for batch fetching
        tickers = [stock['ticker'] for stock in self.stocks]
        
        # Batch fetch all stock info with caching
        if tickers:
            all_stock_info = get_multiple_stocks_cached(tickers)
        else:
            all_stock_info = {}
        
        for stock in self.stocks:
            ticker = stock['ticker']
            quantity = stock['quantity']
        
            try:
                # Get stock info from batch results
                stock_info = all_stock_info.get(ticker, {})
                
                # Get current and historical data
                current_price = stock_info.get('currentPrice', 0)
                previous_close = stock_info.get('previousClose', current_price)
                daily_change = current_price - previous_close
                daily_change_pct = (daily_change / previous_close * 100) if previous_close > 0 else 0
                
                # Get 52-week data
                week_52_high = stock_info.get('fiftyTwoWeekHigh', 0)
                week_52_low = stock_info.get('fiftyTwoWeekLow', 0)
                
                # Get dividend information
                dividend_rate = stock_info.get('dividendRate', 0) or 0
                dividend_yield = stock_info.get('dividendYield', 0) or 0
                annual_dividend_income = dividend_rate * quantity if dividend_rate else 0
                
                # Calculate total value
                total_value = quantity * current_price
                
                # Get company name
                company_name = stock_info.get('longName', ticker)
                
                stock_data = {
                    'ticker': ticker,
                    'company_name': company_name,
                    'quantity': quantity,
                    'current_price': current_price,
                    'previous_close': previous_close,
                    'daily_change': daily_change,
                    'daily_change_pct': daily_change_pct,
                    'total_value': total_value,
                    'week_52_high': week_52_high,
                    'week_52_low': week_52_low,
                    'dividend_rate': dividend_rate,
                    'dividend_yield': dividend_yield * 100 if dividend_yield else 0,  # Convert to percentage
                    'annual_dividend_income': annual_dividend_income
                }
                portfolio_data.append(stock_data)
                
            except Exception as e:
                print(f"Error fetching data for {ticker}: {str(e)}")
                # Add basic data if detailed fetch fails
                stock_data = {
                    'ticker': ticker,
                    'company_name': ticker,
                    'quantity': quantity,
                    'current_price': 0,
                    'previous_close': 0,
                    'daily_change': 0,
                    'daily_change_pct': 0,
                    'total_value': 0,
                    'week_52_high': 0,
                    'week_52_low': 0,
                    'dividend_rate': 0,
                    'dividend_yield': 0,
                    'annual_dividend_income': 0
                }
                portfolio_data.append(stock_data)

        print(f"Portfolio Data: {portfolio_data}")
    
        return portfolio_data
    
    def get_portfolio_summary(self):
        """Calculate comprehensive portfolio metrics"""
        portfolio_data = self.get_portfolio_data()
        
        if not portfolio_data:
            return {
                'total_value': 0,
                'total_cost': 0,
                'total_gain_loss': 0,
                'total_gain_loss_pct': 0,
                'daily_change': 0,
                'daily_change_pct': 0,
                'total_dividend_income': 0,
                'average_dividend_yield': 0,
                'diversification': {},
                'top_performer': None,
                'worst_performer': None
            }
        
        # Calculate totals
        total_value = sum(stock['total_value'] for stock in portfolio_data)
        total_dividend_income = sum(stock['annual_dividend_income'] for stock in portfolio_data)
        daily_change = sum(stock['daily_change'] * stock['quantity'] for stock in portfolio_data)
        
        # Calculate weighted average dividend yield
        weighted_dividend_yield = 0
        if total_value > 0:
            for stock in portfolio_data:
                weight = stock['total_value'] / total_value
                weighted_dividend_yield += stock['dividend_yield'] * weight
        
        # Calculate daily change percentage
        total_previous_value = sum(stock['previous_close'] * stock['quantity'] for stock in portfolio_data)
        daily_change_pct = (daily_change / total_previous_value * 100) if total_previous_value > 0 else 0
        
        # Calculate diversification
        diversification = {}
        for stock in portfolio_data:
            if total_value > 0:
                diversification[stock['ticker']] = {
                    'percentage': (stock['total_value'] / total_value) * 100,
                    'value': stock['total_value']
                }
        
        # Find top and worst performers by daily change percentage
        performers = sorted(portfolio_data, key=lambda x: x['daily_change_pct'], reverse=True)
        top_performer = performers[0] if performers and performers[0]['daily_change_pct'] > 0 else None
        worst_performer = performers[-1] if performers and performers[-1]['daily_change_pct'] < 0 else None
        
        return {
            'total_value': total_value,
            'daily_change': daily_change,
            'daily_change_pct': daily_change_pct,
            'total_dividend_income': total_dividend_income,
            'average_dividend_yield': weighted_dividend_yield,
            'diversification': diversification,
            'top_performer': top_performer,
            'worst_performer': worst_performer,
            'stock_count': len(portfolio_data)
        }

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
        
        # Get all tickers for batch fetching
        tickers = [stock['ticker'] for stock in self.stocks]
        
        # Batch fetch all stock info with caching
        if tickers:
            all_stock_info = get_multiple_stocks_cached(tickers)
        else:
            return 0
        
        for stock in self.stocks:
            ticker = stock['ticker']
            quantity = stock['quantity']
        
            try:
                # Get cached stock info
                stock_info = all_stock_info.get(ticker, {})
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
        # Retrieve the stock data from the database using parameterized query
        query = "SELECT * FROM preprocessed_stock_data WHERE ticker = ?"
        stock_data = pd.read_sql_query(query, self.conn, params=[ticker])
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
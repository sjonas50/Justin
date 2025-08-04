import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database manager that supports both SQLite and PostgreSQL"""
    
    def __init__(self, database_url=None):
        self.database_url = database_url or os.environ.get('DATABASE_URL')
        self.is_postgres = False
        
        if self.database_url and (self.database_url.startswith('postgres://') or 
                                  self.database_url.startswith('postgresql://')):
            self.is_postgres = True
            # Fix for Heroku/Vercel postgres URLs
            if self.database_url.startswith('postgres://'):
                self.database_url = self.database_url.replace('postgres://', 'postgresql://', 1)
        else:
            # Use SQLite for local development
            self.database_url = database_url or 'stock_database.db'
    
    @contextmanager
    def get_connection(self):
        """Get a database connection with context manager"""
        conn = None
        try:
            if self.is_postgres:
                conn = psycopg2.connect(self.database_url)
            else:
                conn = sqlite3.connect(self.database_url)
                conn.row_factory = sqlite3.Row
            yield conn
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        """Execute a query and optionally fetch results"""
        with self.get_connection() as conn:
            if self.is_postgres:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
            else:
                cursor = conn.cursor()
            
            # Convert parameter placeholders for PostgreSQL
            if self.is_postgres and query:
                query = self._convert_placeholders(query)
            
            cursor.execute(query, params or ())
            
            if fetch_one:
                result = cursor.fetchone()
                if not self.is_postgres and result:
                    # Convert SQLite Row to dict
                    result = dict(result)
                return result
            elif fetch_all:
                results = cursor.fetchall()
                if not self.is_postgres:
                    # Convert SQLite Rows to dicts
                    results = [dict(row) for row in results]
                return results
            else:
                conn.commit()
                return cursor.rowcount
    
    def _convert_placeholders(self, query):
        """Convert SQLite ? placeholders to PostgreSQL %s placeholders"""
        return query.replace('?', '%s')
    
    def create_tables(self):
        """Create all necessary tables"""
        # User profiles table
        if self.is_postgres:
            user_profiles_sql = """
            CREATE TABLE IF NOT EXISTS user_profiles (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                age INTEGER,
                investment_amount DECIMAL(10, 2),
                goal1 TEXT,
                goal2 TEXT,
                goal3 TEXT,
                target_age INTEGER,
                target_portfolio_value DECIMAL(12, 2),
                target_dividend_income DECIMAL(10, 2)
            )
            """
        else:
            user_profiles_sql = """
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                age INTEGER,
                investment_amount REAL,
                goal1 TEXT,
                goal2 TEXT,
                goal3 TEXT,
                target_age INTEGER,
                target_portfolio_value REAL,
                target_dividend_income REAL
            )
            """
        
        # Portfolio table
        if self.is_postgres:
            portfolio_sql = """
            CREATE TABLE IF NOT EXISTS portfolio (
                id SERIAL PRIMARY KEY,
                ticker VARCHAR(10),
                quantity INTEGER,
                UNIQUE(ticker)
            )
            """
        else:
            portfolio_sql = """
            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT,
                quantity INTEGER,
                UNIQUE(ticker)
            )
            """
        
        # Execute table creation
        try:
            self.execute_query(user_profiles_sql)
            self.execute_query(portfolio_sql)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise
    
    def save_user_profile(self, name, age, investment_amount, goal1, goal2, goal3,
                          target_age, target_portfolio_value, target_dividend_income):
        """Save user profile (single user system - replaces existing)"""
        # Delete existing profile
        self.execute_query("DELETE FROM user_profiles")
        
        # Insert new profile
        query = """
            INSERT INTO user_profiles (name, age, investment_amount, goal1, goal2, goal3,
                                       target_age, target_portfolio_value, target_dividend_income)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (name, age, investment_amount, goal1, goal2, goal3,
                  target_age, target_portfolio_value, target_dividend_income)
        
        self.execute_query(query, params)
    
    def retrieve_user_profile(self):
        """Retrieve the latest user profile"""
        query = """
            SELECT * FROM user_profiles
            ORDER BY id DESC
            LIMIT 1
        """
        return self.execute_query(query, fetch_one=True)
    
    def get_portfolio(self):
        """Get all stocks in portfolio"""
        query = "SELECT ticker, quantity FROM portfolio"
        return self.execute_query(query, fetch_all=True)
    
    def add_stock(self, ticker, quantity):
        """Add or update stock in portfolio"""
        if self.is_postgres:
            # PostgreSQL UPSERT
            query = """
                INSERT INTO portfolio (ticker, quantity)
                VALUES (%s, %s)
                ON CONFLICT (ticker)
                DO UPDATE SET quantity = portfolio.quantity + EXCLUDED.quantity
            """
        else:
            # SQLite - check if exists first
            existing = self.execute_query(
                "SELECT quantity FROM portfolio WHERE ticker = ?",
                (ticker,),
                fetch_one=True
            )
            if existing:
                query = "UPDATE portfolio SET quantity = quantity + ? WHERE ticker = ?"
                params = (quantity, ticker)
            else:
                query = "INSERT INTO portfolio (ticker, quantity) VALUES (?, ?)"
                params = (ticker, quantity)
            
            self.execute_query(query, params)
            return
        
        self.execute_query(query, (ticker, quantity))
    
    def remove_stock(self, ticker):
        """Remove stock from portfolio"""
        query = "DELETE FROM portfolio WHERE ticker = ?"
        self.execute_query(query, (ticker,))
    
    def update_stock_quantity(self, ticker, quantity):
        """Update stock quantity"""
        query = "UPDATE portfolio SET quantity = ? WHERE ticker = ?"
        self.execute_query(query, (quantity, ticker))
    
    def clear_portfolio(self):
        """Clear all stocks from portfolio"""
        self.execute_query("DELETE FROM portfolio")

# Singleton instance
_db_manager = None

def get_db_manager():
    """Get or create database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
#!/usr/bin/env python3
"""
Database migration script to help migrate data from SQLite to PostgreSQL
"""
import sqlite3
import os
from db_manager import get_db_manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_from_sqlite():
    """Migrate data from SQLite databases to the configured database"""
    db_manager = get_db_manager()
    
    # Create tables in the target database
    logger.info("Creating tables in target database...")
    db_manager.create_tables()
    
    # Migrate user profiles if SQLite file exists
    if os.path.exists('user_profiles.db'):
        logger.info("Migrating user profiles...")
        sqlite_conn = sqlite3.connect('user_profiles.db')
        sqlite_conn.row_factory = sqlite3.Row
        cursor = sqlite_conn.cursor()
        
        cursor.execute("SELECT * FROM user_profiles ORDER BY id DESC LIMIT 1")
        profile = cursor.fetchone()
        
        if profile:
            db_manager.save_user_profile(
                profile['name'],
                profile['age'],
                profile['investment_amount'],
                profile['goal1'],
                profile['goal2'],
                profile['goal3'],
                profile['target_age'],
                profile['target_portfolio_value'],
                profile['target_dividend_income']
            )
            logger.info("User profile migrated successfully")
        
        sqlite_conn.close()
    
    # Migrate portfolio data if SQLite file exists
    if os.path.exists('stock_database.db'):
        logger.info("Migrating portfolio data...")
        sqlite_conn = sqlite3.connect('stock_database.db')
        sqlite_conn.row_factory = sqlite3.Row
        cursor = sqlite_conn.cursor()
        
        try:
            cursor.execute("SELECT ticker, quantity FROM portfolio")
            stocks = cursor.fetchall()
            
            for stock in stocks:
                db_manager.add_stock(stock['ticker'], stock['quantity'])
                logger.info(f"Migrated stock: {stock['ticker']} - {stock['quantity']} shares")
            
            logger.info("Portfolio data migrated successfully")
        except sqlite3.OperationalError as e:
            logger.warning(f"Could not migrate portfolio: {e}")
        
        sqlite_conn.close()
    
    logger.info("Migration completed!")

if __name__ == "__main__":
    migrate_from_sqlite()
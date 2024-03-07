import pandas as pd
import numpy as np
import sqlite3
from data_retrieval import get_stock_data

def clean_missing_values(data):
    # Drop rows with missing values
    cleaned_data = data.dropna()
    return cleaned_data

def normalize_data(data):
    # Normalize the data using min-max scaling
    normalized_data = (data - data.min()) / (data.max() - data.min())
    return normalized_data

def extract_features(data):
    # Extract relevant features from the stock data
    features = data[['Open', 'High', 'Low', 'Close', 'Volume']]
    return features

def create_database_connection(db_name):
    # Create a connection to the SQLite database
    conn = sqlite3.connect(db_name)
    return conn

def store_data_to_database(conn, data, table_name):
    # Store the preprocessed data to the database
    data.to_sql(table_name, conn, if_exists='replace', index=False)

def preprocess_data(raw_data):
    # Clean missing values
    cleaned_data = clean_missing_values(raw_data)
    
    # Normalize the data
    normalized_data = normalize_data(cleaned_data)
    
    # Extract features
    features = extract_features(normalized_data)
    
    return features

def main():
    # Retrieve the stock data using the get_stock_data() function
    ticker = "AAPL"  # Replace with the desired stock ticker
    start_date = "2022-01-01"  # Replace with the desired start date
    end_date = "2023-06-07"  # Replace with the desired end date
    stock_data = get_stock_data(ticker, start_date, end_date)
    
    # Preprocess the stock data
    preprocessed_data = preprocess_data(stock_data)
    
    # Add the ticker column to the preprocessed data
    preprocessed_data['ticker'] = ticker
    
    # Create a database connection
    db_name = 'stock_database.db'
    conn = create_database_connection(db_name)
    
    # Store the preprocessed data to the database
    table_name = 'preprocessed_stock_data'
    store_data_to_database(conn, preprocessed_data, table_name)
    
    # Close the database connection
    conn.close()

if __name__ == '__main__':
    main()
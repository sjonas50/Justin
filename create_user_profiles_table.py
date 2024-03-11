import sqlite3

def create_user_profiles_table():
    # Create a connection to the database
    conn = sqlite3.connect('user_profiles.db')
    cursor = conn.cursor()
    
    # Create the user_profiles table
    cursor.execute('''
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
    ''')
    
    conn.commit()
    conn.close()

# Call the function to create the user_profiles table
create_user_profiles_table()
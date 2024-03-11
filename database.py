import sqlite3

def create_database_connection(db_name):
    conn = sqlite3.connect(db_name)
    return conn

def save_user_profile(name, age, investment_amount, goal1, goal2, goal3,
                      target_age, target_portfolio_value, target_dividend_income):
    # Create a connection to the database
    conn = create_database_connection('user_profiles.db')
    cursor = conn.cursor()
    
    # Insert the user profile into the database
    cursor.execute('''
        INSERT INTO user_profiles (name, age, investment_amount, goal1, goal2, goal3,
                                   target_age, target_portfolio_value, target_dividend_income)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, age, investment_amount, goal1, goal2, goal3,
          target_age, target_portfolio_value, target_dividend_income))
    
    conn.commit()
    conn.close()

# Add other database-related functions here, such as retrieving user profiles, updating profiles, etc.
def retrieve_user_profile():
    # Create a connection to the database
    conn = create_database_connection('user_profiles.db')
    cursor = conn.cursor()
    
    # Retrieve the latest user profile from the database
    cursor.execute('''
        SELECT * FROM user_profiles
        ORDER BY id DESC
        LIMIT 1
    ''')
    
    user_profile = cursor.fetchone()
    
    conn.close()
    
    if user_profile:
        return {
            'name': user_profile[1],
            'age': user_profile[2],
            'investment_amount': user_profile[3],
            'goal1': user_profile[4],
            'goal2': user_profile[5],
            'goal3': user_profile[6],
            'target_age': user_profile[7],
            'target_portfolio_value': user_profile[8],
            'target_dividend_income': user_profile[9]
        }
    else:
        return None
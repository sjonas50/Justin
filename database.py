import sqlite3

def create_database_connection(db_name):
    conn = sqlite3.connect(db_name)
    return conn

def save_user_profile(name, age, investment_amount, goal1, goal2, goal3,
                      target_age, target_portfolio_value, target_dividend_income):
    """Save user profile with validation and error handling"""
    from utils import validate_text, validate_age, validate_number
    
    # Validate inputs
    valid, name = validate_text(name, "Name", max_length=100)
    if not valid:
        raise ValueError(name)
    
    valid, age = validate_age(age)
    if not valid:
        raise ValueError(age)
    
    valid, investment_amount = validate_number(investment_amount, "Investment amount", min_val=0, max_val=10000000)
    if not valid:
        raise ValueError(investment_amount)
    
    valid, goal1 = validate_text(goal1, "Goal 1")
    if not valid:
        raise ValueError(goal1)
    
    valid, goal2 = validate_text(goal2, "Goal 2")
    if not valid:
        raise ValueError(goal2)
    
    valid, goal3 = validate_text(goal3, "Goal 3")
    if not valid:
        raise ValueError(goal3)
    
    valid, target_age = validate_age(target_age)
    if not valid:
        raise ValueError(target_age)
    
    valid, target_portfolio_value = validate_number(target_portfolio_value, "Target portfolio value", min_val=0, max_val=100000000)
    if not valid:
        raise ValueError(target_portfolio_value)
    
    valid, target_dividend_income = validate_number(target_dividend_income, "Target dividend income", min_val=0, max_val=1000000)
    if not valid:
        raise ValueError(target_dividend_income)
    
    # Create a connection to the database
    conn = create_database_connection('user_profiles.db')
    cursor = conn.cursor()
    
    try:
        # Delete any existing profile (single user system)
        cursor.execute('DELETE FROM user_profiles')
        
        # Insert the user profile into the database
        cursor.execute('''
            INSERT INTO user_profiles (name, age, investment_amount, goal1, goal2, goal3,
                                       target_age, target_portfolio_value, target_dividend_income)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, age, investment_amount, goal1, goal2, goal3,
              target_age, target_portfolio_value, target_dividend_income))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
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
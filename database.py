import sqlite3
from db_manager import get_db_manager

def create_database_connection(db_name):
    """Legacy function for backward compatibility"""
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
    
    # Use the new database manager
    db_manager = get_db_manager()
    db_manager.save_user_profile(name, age, investment_amount, goal1, goal2, goal3,
                                 target_age, target_portfolio_value, target_dividend_income)

def retrieve_user_profile():
    """Retrieve the latest user profile from the database"""
    db_manager = get_db_manager()
    user_profile = db_manager.retrieve_user_profile()
    
    if user_profile:
        return {
            'name': user_profile.get('name'),
            'age': user_profile.get('age'),
            'investment_amount': user_profile.get('investment_amount'),
            'goal1': user_profile.get('goal1'),
            'goal2': user_profile.get('goal2'),
            'goal3': user_profile.get('goal3'),
            'target_age': user_profile.get('target_age'),
            'target_portfolio_value': user_profile.get('target_portfolio_value'),
            'target_dividend_income': user_profile.get('target_dividend_income')
        }
    else:
        return None
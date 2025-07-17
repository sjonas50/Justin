import re
from typing import Union, Tuple

def validate_ticker(ticker: str) -> Tuple[bool, str]:
    """Validate stock ticker symbol"""
    if not ticker:
        return False, "Ticker symbol is required"
    
    # Remove whitespace
    ticker = ticker.strip().upper()
    
    # Check length (NYSE/NASDAQ tickers are 1-5 characters)
    if not 1 <= len(ticker) <= 5:
        return False, "Ticker must be 1-5 characters"
    
    # Check for valid characters (letters and sometimes numbers)
    if not re.match(r'^[A-Z0-9]+$', ticker):
        return False, "Ticker must contain only letters and numbers"
    
    return True, ticker

def validate_quantity(quantity: Union[str, int]) -> Tuple[bool, Union[int, str]]:
    """Validate stock quantity"""
    try:
        qty = int(quantity)
        if qty <= 0:
            return False, "Quantity must be positive"
        if qty > 1000000:  # Reasonable upper limit
            return False, "Quantity is too large"
        return True, qty
    except (ValueError, TypeError):
        return False, "Quantity must be a valid number"

def validate_number(value: Union[str, float], field_name: str, min_val: float = 0, max_val: float = float('inf')) -> Tuple[bool, Union[float, str]]:
    """Validate numeric input"""
    try:
        num = float(value)
        if num < min_val:
            return False, f"{field_name} must be at least {min_val}"
        if num > max_val:
            return False, f"{field_name} must be at most {max_val}"
        return True, num
    except (ValueError, TypeError):
        return False, f"{field_name} must be a valid number"

def validate_age(age: Union[str, int]) -> Tuple[bool, Union[int, str]]:
    """Validate age input"""
    try:
        age_int = int(age)
        if age_int < 0 or age_int > 150:
            return False, "Age must be between 0 and 150"
        return True, age_int
    except (ValueError, TypeError):
        return False, "Age must be a valid number"

def validate_text(text: str, field_name: str, max_length: int = 200) -> Tuple[bool, str]:
    """Validate text input"""
    if not text or not text.strip():
        return False, f"{field_name} is required"
    
    text = text.strip()
    
    if len(text) > max_length:
        return False, f"{field_name} must be at most {max_length} characters"
    
    # Basic XSS prevention - remove potentially harmful characters
    cleaned_text = re.sub(r'[<>\"\'&]', '', text)
    
    return True, cleaned_text

def sanitize_sql_identifier(identifier: str) -> str:
    """Sanitize SQL identifiers (table names, column names)"""
    # Only allow alphanumeric characters and underscores
    return re.sub(r'[^a-zA-Z0-9_]', '', identifier)
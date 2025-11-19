"""Number parser utility for handling market size strings"""

import re
from typing import Union


def parse_market_number(value: str) -> float:
    """
    Parse market size strings like '3.2B', '4.1M', '500K' to float
    
    Examples:
        '3.2B USD' -> 3.2
        '4.1B' -> 4.1
        '500M' -> 500.0
        '1.5K' -> 1.5
        '3.2' -> 3.2
    
    Args:
        value: String containing number with optional suffix (B, M, K)
    
    Returns:
        Float value without suffix
    """
    if not value or not isinstance(value, str):
        return 0.0
    
    # Remove common words and extra spaces
    value = value.upper().strip()
    value = value.replace('USD', '').replace('$', '').replace('€', '').replace('EUR', '').strip()
    
    # Extract number and suffix using regex
    match = re.match(r'([0-9.]+)\s*([BMK])?', value)
    
    if not match:
        # Try to convert directly
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    number_str = match.group(1)
    suffix = match.group(2) if match.group(2) else ''
    
    try:
        number = float(number_str)
    except (ValueError, TypeError):
        return 0.0
    
    # Don't multiply - just return the base number
    # '3.2B' -> 3.2 (not 3200000000)
    return number


def parse_percentage(value: str) -> float:
    """
    Parse percentage strings like '15%', '18% CAGR' to float
    
    Examples:
        '15%' -> 15.0
        '18% CAGR' -> 18.0
        '15' -> 15.0
    
    Args:
        value: String containing percentage
    
    Returns:
        Float value without % sign
    """
    if not value or not isinstance(value, str):
        return 0.0
    
    # Remove common words
    value = value.upper().strip()
    value = value.replace('CAGR', '').replace('%', '').strip()
    
    # Extract first number
    match = re.match(r'([0-9.]+)', value)
    
    if not match:
        return 0.0
    
    try:
        return float(match.group(1))
    except (ValueError, TypeError):
        return 0.0


def safe_float(value: Union[str, float, int], default: float = 0.0) -> float:
    """
    Safely convert any value to float with fallback
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
    
    Returns:
        Float value or default
    """
    if isinstance(value, (int, float)):
        return float(value)
    
    if isinstance(value, str):
        return parse_market_number(value)
    
    return default

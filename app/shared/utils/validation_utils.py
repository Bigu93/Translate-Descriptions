"""
Utility functions for input validation and sanitization.
"""
import re
from typing import Optional


def validate_email(email: str) -> bool:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if email is valid, False otherwise

    Example:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("invalid-email")
        False
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format.

    Args:
        phone: Phone number to validate

    Returns:
        True if phone is valid, False otherwise

    Example:
        >>> validate_phone("+1234567890")
        True
        >>> validate_phone("123")
        False
    """
    # Remove all non-digit characters except + at start
    cleaned = re.sub(r'[^\d+]', '', phone)
    return len(cleaned) >= 7 and len(cleaned) <= 15


def sanitize_input(input_str: str) -> str:
    """
    Sanitize user input to prevent injection attacks.

    Args:
        input_str: Input string to sanitize

    Returns:
        Sanitized string

    Example:
        >>> sanitize_input("<script>alert('xss')</script>")
        '<script>alert('xss')</script>'
    """
    sanitized = re.sub(r'[<>]', '', input_str)
    sanitized = sanitized.replace('"', '"').replace("'", '\'')
    return sanitized.strip()


def validate_url(url: str) -> bool:
    """
    Validate URL format.

    Args:
        url: URL to validate

    Returns:
        True if URL is valid, False otherwise

    Example:
        >>> validate_url("https://example.com")
        True
        >>> validate_url("not-a-url")
        False
    """
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return re.match(pattern, url) is not None


def validate_numeric(value: str, min_val: int = 0, max_val: int = 999999) -> bool:
    """
    Validate numeric value within range.

    Args:
        value: String value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Returns:
        True if value is numeric and within range, False otherwise

    Example:
        >>> validate_numeric("100", 0, 1000)
        True
        >>> validate_numeric("abc", 0, 1000)
        False
    """
    try:
        num = int(value)
        return min_val <= num <= max_val
    except (ValueError, TypeError):
        return False


def validate_string_length(
    value: str,
    min_length: int = 1,
    max_length: int = 255
) -> bool:
    """
    Validate string length within range.

    Args:
        value: String value to validate
        min_length: Minimum allowed length
        max_length: Maximum allowed length

    Returns:
        True if value length is within range, False otherwise

    Example:
        >>> validate_string_length("hello", 1, 10)
        True
        >>> validate_string_length("", 1, 10)
        False
    """
    return min_length <= len(value) <= max_length


def validate_required_fields(data: dict, required_fields: list) -> Optional[str]:
    """
    Validate that all required fields are present in data.

    Args:
        data: Dictionary to validate
        required_fields: List of required field names

    Returns:
        Error message if validation fails, None otherwise

    Example:
        >>> validate_required_fields({"name": "John"}, ["name", "email"])
        'email is required'
        >>> validate_required_fields({"name": "John", "email": "test@example.com"}, ["name", "email"])
        None
    """
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return f"{', '.join(missing_fields)} {'is' if len(missing_fields) == 1 else 'are'} required"
    return None

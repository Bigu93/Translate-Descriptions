"""
JSON parsing utilities for handling OpenAI API responses.
"""
import json
from typing import Any, Dict, List, Optional
from app.infrastructure.logging.structured_logger import get_logger
from app.core.domain.exceptions import ParsingError


logger = get_logger("json_parser")


def escape_single_quotes(value: str) -> str:
    """
    Escape single quotes in a string value to ensure valid JSON format.

    Args:
        value: The string value to escape

    Returns:
        The string with escaped single quotes

    Example:
        >>> escape_single_quotes("John's book")
        "John\\'s book"
    """
    return value.replace("'", "\\'")


def ensure_quotes_and_escape(json_obj: Any) -> Any:
    """
    Recursively ensure all keys and values are correctly quoted and single quotes in values are escaped.

    This function operates on the parsed JSON object (dict/list).

    Args:
        json_obj: The JSON object to process (dict, list, str, or primitive)

    Returns:
        The processed JSON object with proper quoting and escaping

    Example:
        >>> data = {"name": "John's", "age": 30}
        >>> ensure_quotes_and_escape(data)
        {'name': "John\\'s", 'age': 30}
    """
    if isinstance(json_obj, dict):
        return {
            ensure_quotes_and_escape(k): ensure_quotes_and_escape(v)
            for k, v in json_obj.items()
        }
    elif isinstance(json_obj, list):
        return [ensure_quotes_and_escape(element) for element in json_obj]
    elif isinstance(json_obj, str):
        return escape_single_quotes(json_obj)
    else:
        return json_obj


def parse_response_content_openai(response_content: str) -> Optional[Dict[str, Any]]:
    """
    Validate and parse the response from OpenAI, ensuring all keys and values are properly formatted.

    This function handles cases where OpenAI returns JSON with potential formatting issues.
    It attempts to extract JSON from the response content and ensures proper formatting.

    Args:
        response_content: The raw response content from OpenAI

    Returns:
        Parsed and corrected JSON as a dictionary, or None if parsing fails

    Raises:
        ParsingError: If the response content cannot be parsed as valid JSON

    Example:
        >>> content = '{"name": "Product", "description": "John\\'s item"}'
        >>> result = parse_response_content_openai(content)
        >>> result["name"]
        'Product'
    """
    try:
        parsed_json = json.loads(response_content)
        corrected_json = ensure_quotes_and_escape(parsed_json)
        return corrected_json
    except json.JSONDecodeError:
        try:
            json_start = response_content.index("{")
            json_end = response_content.rindex("}") + 1
            json_str = response_content[json_start:json_end]
            parsed_json = json.loads(json_str)
            corrected_json = ensure_quotes_and_escape(parsed_json)
            return corrected_json
        except (ValueError, json.JSONDecodeError) as e:
            logger.error(f"Error in extracting or parsing JSON: {e}")
            logger.error(f"Response content: {response_content[:500]}...")
            raise ParsingError(f"Failed to parse JSON response: {e}") from e


def parse_json_response(response_data: Any) -> Dict[str, Any]:
    """
    Parse JSON response data with error handling.

    Args:
        response_data: The response data to parse (can be string or dict)

    Returns:
        Parsed JSON as a dictionary

    Raises:
        ParsingError: If the response data cannot be parsed

    Example:
        >>> data = '{"key": "value"}'
        >>> result = parse_json_response(data)
        >>> result["key"]
        'value'
    """
    if isinstance(response_data, dict):
        return response_data

    try:
        return json.loads(response_data)
    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f"Failed to parse JSON response: {e}")
        raise ParsingError(f"Invalid JSON response: {e}") from e


def validate_json_structure(
    data: Dict[str, Any], required_keys: List[str]
) -> bool:
    """
    Validate that a JSON dictionary contains all required keys.

    Args:
        data: The JSON data to validate
        required_keys: List of required keys

    Returns:
        True if all required keys are present, False otherwise

    Example:
        >>> data = {"name": "Product", "price": 10.99}
        >>> validate_json_structure(data, ["name", "price"])
        True
        >>> validate_json_structure(data, ["name", "price", "description"])
        False
    """
    return all(key in data for key in required_keys)


def sanitize_json_output(data: Any) -> Any:
    """
    Sanitize JSON output by removing None values and empty structures.

    Args:
        data: The data to sanitize

    Returns:
        Sanitized data

    Example:
        >>> data = {"name": "Product", "description": None, "tags": []}
        >>> sanitize_json_output(data)
        {'name': 'Product'}
    """
    if isinstance(data, dict):
        return {
            k: sanitize_json_output(v)
            for k, v in data.items()
            if v is not None and v != [] and v != {}
        }
    elif isinstance(data, list):
        return [sanitize_json_output(item) for item in data if item is not None]
    else:
        return data

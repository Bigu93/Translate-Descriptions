"""
Error handling utilities for API responses.
"""
import traceback
from typing import Tuple, Any
from flask import jsonify
from app.infrastructure.logging.structured_logger import get_logger
from app.core.domain.exceptions import (
    TranslationError,
    AuthenticationError,
    ValidationError,
    ExternalAPIError,
    ParsingError,
    RepositoryError,
    ConfigurationError,
)


logger_server_error = get_logger("server_error")
logger_invalid_json = get_logger("invalid_json")


def handle_internal_server_error(error: Exception) -> Tuple[Any, int]:
    """
    Handle internal server errors with logging.

    Args:
        error: The exception that occurred

    Returns:
        Tuple of (JSON response, status code 500)

    Example:
        >>> try:
        ...     risky_operation()
        ... except Exception as e:
        ...     return handle_internal_server_error(e)
    """
    logger_server_error.error(f"Error: {str(error)}")
    logger_server_error.error("Traceback: " + traceback.format_exc())
    return jsonify(error="Internal Server Error"), 500


def handle_invalid_json_format(error: Exception) -> Tuple[Any, int]:
    """
    Handle invalid JSON format errors with logging.

    Args:
        error: The JSON parsing exception

    Returns:
        Tuple of (JSON response, status code 400)

    Example:
        >>> try:
        ...     json.loads(invalid_json)
        ... except json.JSONDecodeError as e:
        ...     return handle_invalid_json_format(e)
    """
    logger_invalid_json.error(f"JSON parsing error: {str(error)}")
    response = "Invalid JSON content"
    logger_invalid_json.error(response)
    return jsonify(error=response), 400


def handle_translation_error(error: TranslationError) -> Tuple[Any, int]:
    """
    Handle translation errors.

    Args:
        error: The translation exception

    Returns:
        Tuple of (JSON response, status code 400)

    Example:
        >>> try:
        ...     translate_text(...)
        ... except TranslationError as e:
        ...     return handle_translation_error(e)
    """
    logger_server_error.error(f"Translation error: {str(error)}")
    return jsonify(error=str(error)), 400


def handle_authentication_error(error: AuthenticationError) -> Tuple[Any, int]:
    """
    Handle authentication errors.

    Args:
        error: The authentication exception

    Returns:
        Tuple of (JSON response, status code 401)

    Example:
        >>> try:
        ...     authenticate_user(...)
        ... except AuthenticationError as e:
        ...     return handle_authentication_error(e)
    """
    logger_server_error.error(f"Authentication error: {str(error)}")
    return jsonify(error=str(error)), 401


def handle_validation_error(error: ValidationError) -> Tuple[Any, int]:
    """
    Handle validation errors.

    Args:
        error: The validation exception

    Returns:
        Tuple of (JSON response, status code 400)

    Example:
        >>> try:
        ...     validate_input(data)
        ... except ValidationError as e:
        ...     return handle_validation_error(e)
    """
    logger_server_error.error(f"Validation error: {str(error)}")
    return jsonify(error=str(error)), 400


def handle_external_api_error(error: ExternalAPIError) -> Tuple[Any, int]:
    """
    Handle external API errors.

    Args:
        error: The external API exception

    Returns:
        Tuple of (JSON response, status code 502)

    Example:
        >>> try:
        ...     call_external_api(...)
        ... except ExternalAPIError as e:
        ...     return handle_external_api_error(e)
    """
    logger_server_error.error(f"External API error: {str(error)}")
    return jsonify(error=str(error)), 502


def handle_parsing_error(error: ParsingError) -> Tuple[Any, int]:
    """
    Handle parsing errors.

    Args:
        error: The parsing exception

    Returns:
        Tuple of (JSON response, status code 400)

    Example:
        >>> try:
        ...     parse_json_data(data)
        ... except ParsingError as e:
        ...     return handle_parsing_error(e)
    """
    logger_invalid_json.error(f"Parsing error: {str(error)}")
    return jsonify(error=str(error)), 400


def handle_repository_error(error: RepositoryError) -> Tuple[Any, int]:
    """
    Handle repository errors.

    Args:
        error: The repository exception

    Returns:
        Tuple of (JSON response, status code 500)

    Example:
        >>> try:
        ...     repository.save(data)
        ... except RepositoryError as e:
        ...     return handle_repository_error(e)
    """
    logger_server_error.error(f"Repository error: {str(error)}")
    return jsonify(error="Database error"), 500


def handle_configuration_error(error: ConfigurationError) -> Tuple[Any, int]:
    """
    Handle configuration errors.

    Args:
        error: The configuration exception

    Returns:
        Tuple of (JSON response, status code 500)

    Example:
        >>> try:
        ...     load_configuration()
        ... except ConfigurationError as e:
        ...     return handle_configuration_error(e)
    """
    logger_server_error.error(f"Configuration error: {str(error)}")
    return jsonify(error="Configuration error"), 500


def handle_generic_error(error: Exception) -> Tuple[Any, int]:
    """
    Handle generic errors by routing to appropriate handler.

    Args:
        error: The exception that occurred

    Returns:
        Tuple of (JSON response, status code)

    Example:
        >>> try:
        ...     some_operation()
        ... except Exception as e:
        ...     return handle_generic_error(e)
    """
    if isinstance(error, TranslationError):
        return handle_translation_error(error)
    elif isinstance(error, AuthenticationError):
        return handle_authentication_error(error)
    elif isinstance(error, ValidationError):
        return handle_validation_error(error)
    elif isinstance(error, ExternalAPIError):
        return handle_external_api_error(error)
    elif isinstance(error, ParsingError):
        return handle_parsing_error(error)
    elif isinstance(error, RepositoryError):
        return handle_repository_error(error)
    elif isinstance(error, ConfigurationError):
        return handle_configuration_error(error)
    else:
        return handle_internal_server_error(error)

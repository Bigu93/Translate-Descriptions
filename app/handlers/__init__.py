"""
Error handlers for API responses.
"""
from app.handlers.error_handlers import (
    handle_internal_server_error,
    handle_invalid_json_format,
    handle_translation_error,
    handle_authentication_error,
    handle_validation_error,
    handle_external_api_error,
    handle_parsing_error,
    handle_repository_error,
    handle_configuration_error,
    handle_generic_error,
)

__all__ = [
    "handle_internal_server_error",
    "handle_invalid_json_format",
    "handle_translation_error",
    "handle_authentication_error",
    "handle_validation_error",
    "handle_external_api_error",
    "handle_parsing_error",
    "handle_repository_error",
    "handle_configuration_error",
    "handle_generic_error",
]

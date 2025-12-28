"""
Custom exception hierarchy for the Translate-Descriptions application.

This module defines a comprehensive exception hierarchy following the Exception Hierarchy Pattern.
All application-specific exceptions inherit from TranslateDescriptionsError for consistent error handling.
"""


class TranslateDescriptionsError(Exception):
    """Base exception for all application errors.
    
    This serves as the root of our exception hierarchy, allowing
    catch-all exception handling for application-specific errors.
    """
    pass


class ValidationError(TranslateDescriptionsError):
    """Raised when input validation fails.
    
    Use this when request data, parameters, or user input
    does not meet the required format or constraints.
    """
    pass


class NotFoundError(TranslateDescriptionsError):
    """Raised when a resource is not found.
    
    Use this when a requested resource (product, token, etc.)
    cannot be located in the system.
    """
    pass


class AuthenticationError(TranslateDescriptionsError):
    """Raised when authentication fails.
    
    Use this when a user or service cannot be authenticated
    due to invalid credentials or tokens.
    """
    pass


class AuthorizationError(TranslateDescriptionsError):
    """Raised when authorization fails.
    
    Use this when an authenticated user does not have permission
    to access a specific resource or perform an action.
    """
    pass


class DatabaseError(TranslateDescriptionsError):
    """Raised when database operation fails.
    
    Use this when SQL queries, connections, or transactions fail.
    """
    pass


class ExternalAPIError(TranslateDescriptionsError):
    """Raised when external API call fails.
    
    Attributes:
        status_code: Optional HTTP status code from the external API
        response: Optional response text from the external API
    """
    
    def __init__(
        self,
        message: str,
        status_code: int = None,
        response: str = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class OpenAIError(ExternalAPIError):
    """Raised when OpenAI API call fails.
    
    Specific subclass for OpenAI-related errors.
    """
    pass


class IdoSellError(ExternalAPIError):
    """Raised when IdoSell API call fails.
    
    Specific subclass for IdoSell-related errors.
    """
    pass


class VIESError(ExternalAPIError):
    """Raised when VIES VAT validation service fails.
    
    Specific subclass for VIES-related errors.
    """
    pass


class TranslationError(TranslateDescriptionsError):
    """Raised when translation operation fails.
    
    Use this when the translation service encounters an error
    during text translation or content generation.
    """
    pass


class CacheError(TranslateDescriptionsError):
    """Raised when cache operation fails.
    
    Use this when reading from or writing to cache fails.
    """
    pass


class ConfigurationError(TranslateDescriptionsError):
    """Raised when configuration is invalid or missing.
    
    Use this when required configuration values are missing
    or have invalid formats.
    """
    pass


class RateLimitExceededError(TranslateDescriptionsError):
    """Raised when rate limit is exceeded.
    
    Use this when a service or endpoint has been called
    more times than allowed within a time window.
    """
    pass


class ParsingError(TranslateDescriptionsError):
    """Raised when parsing operation fails.
    
    Use this when data cannot be parsed from one format to another,
    such as JSON parsing, XML parsing, or data structure validation.
    """
    pass


class RepositoryError(TranslateDescriptionsError):
    """Raised when repository operation fails.
    
    Use this when data access layer operations fail,
    such as queries, updates, or deletes in the repository pattern.
    """
    pass

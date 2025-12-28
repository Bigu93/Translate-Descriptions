"""
Authentication middleware for protecting API routes.
"""
from typing import Callable, Any
from flask import request, jsonify
from functools import wraps
from app.infrastructure.logging.structured_logger import get_logger
from app.core.domain.exceptions import AuthenticationError


logger = get_logger("auth_middleware")


def require_auth(auth_func: Callable[[str], bool]) -> Callable:
    """
    Decorator to require authentication for a route.

    Args:
        auth_func: Function that validates the authentication token

    Returns:
        Decorator function

    Example:
        >>> @require_auth(validate_token)
        ... def protected_route():
        ...     return {"message": "Authenticated"}
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            auth_header = request.headers.get("Authorization")

            if not auth_header:
                logger.warning("Missing Authorization header")
                return jsonify(error="Missing Authorization header"), 401

            if not auth_header.startswith("Bearer "):
                logger.warning("Invalid Authorization header format")
                return jsonify(error="Invalid Authorization header format"), 401

            token = auth_header[7:]  # Remove "Bearer " prefix

            try:
                if not auth_func(token):
                    logger.warning(f"Invalid token: {token[:10]}...")
                    return jsonify(error="Invalid or expired token"), 401
            except AuthenticationError as e:
                logger.error(f"Authentication error: {e}")
                return jsonify(error=str(e)), 401
            except Exception as e:
                logger.error(f"Unexpected error during authentication: {e}")
                return jsonify(error="Authentication failed"), 500

            return f(*args, **kwargs)

        return decorated_function
    return decorator


def require_api_key(api_key_func: Callable[[str], bool]) -> Callable:
    """
    Decorator to require API key for a route.

    Args:
        api_key_func: Function that validates the API key

    Returns:
        Decorator function

    Example:
        >>> @require_api_key(validate_api_key)
        ... def protected_route():
        ...     return {"message": "Authenticated"}
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            api_key = request.headers.get("X-API-Key") or request.args.get("api_key")

            if not api_key:
                logger.warning("Missing API key")
                return jsonify(error="Missing API key"), 401

            try:
                if not api_key_func(api_key):
                    logger.warning(f"Invalid API key: {api_key[:10]}...")
                    return jsonify(error="Invalid API key"), 401
            except Exception as e:
                logger.error(f"Unexpected error during API key validation: {e}")
                return jsonify(error="API key validation failed"), 500

            return f(*args, **kwargs)

        return decorated_function
    return decorator


def require_admin(admin_check_func: Callable[[str], bool]) -> Callable:
    """
    Decorator to require admin privileges for a route.

    Args:
        admin_check_func: Function that checks if user has admin privileges

    Returns:
        Decorator function

    Example:
        >>> @require_admin(check_admin)
        ... def admin_route():
        ...     return {"message": "Admin access granted"}
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            auth_header = request.headers.get("Authorization")

            if not auth_header:
                logger.warning("Missing Authorization header for admin route")
                return jsonify(error="Missing Authorization header"), 401

            if not auth_header.startswith("Bearer "):
                logger.warning("Invalid Authorization header format for admin route")
                return jsonify(error="Invalid Authorization header format"), 401

            token = auth_header[7:]

            try:
                if not admin_check_func(token):
                    logger.warning(f"Admin access denied for token: {token[:10]}...")
                    return jsonify(error="Admin privileges required"), 403
            except AuthenticationError as e:
                logger.error(f"Authentication error: {e}")
                return jsonify(error=str(e)), 401
            except Exception as e:
                logger.error(f"Unexpected error during admin check: {e}")
                return jsonify(error="Admin check failed"), 500

            return f(*args, **kwargs)

        return decorated_function
    return decorator

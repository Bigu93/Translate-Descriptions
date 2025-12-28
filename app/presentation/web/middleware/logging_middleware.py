"""
Logging middleware for request/response logging.
"""
import time
from typing import Callable, Any
from flask import request, g
from functools import wraps
from app.infrastructure.logging.structured_logger import get_logger


logger = get_logger("request_logging")


def log_request_response(f: Callable) -> Callable:
    """
    Decorator to log incoming requests and outgoing responses.

    Args:
        f: The function to decorate

    Returns:
        Decorated function with logging

    Example:
        >>> @log_request_response
        ... def my_route():
        ...     return {"message": "Hello"}
    """
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()

        # Log request
        logger.info(
            f"Incoming request: {request.method} {request.path} "
            f"from {request.remote_addr}"
        )

        # Store request details in Flask's g object
        g.request_start_time = start_time
        g.request_method = request.method
        g.request_path = request.path

        try:
            response = f(*args, **kwargs)

            # Calculate duration
            duration = time.time() - start_time

            # Log response
            logger.info(
                f"Request completed: {request.method} {request.path} "
                f"status: {response[1] if isinstance(response, tuple) else 200} "
                f"duration: {duration:.3f}s"
            )

            return response
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.path} "
                f"error: {str(e)} duration: {duration:.3f}s"
            )
            raise

    return decorated_function


def log_request_details(f: Callable) -> Callable:
    """
    Decorator to log detailed request information including headers and body.

    Args:
        f: The function to decorate

    Returns:
        Decorated function with detailed logging

    Example:
        >>> @log_request_details
        ... def my_route():
        ...     return {"message": "Hello"}
    """
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()

        # Log detailed request information
        logger.debug(
            f"Request details:\n"
            f"  Method: {request.method}\n"
            f"  Path: {request.path}\n"
            f"  Query: {dict(request.args)}\n"
            f"  Headers: {dict(request.headers)}\n"
            f"  Remote Addr: {request.remote_addr}"
        )

        # Log request body if present (for POST/PUT)
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                if request.is_json:
                    logger.debug(f"Request Body: {request.get_json()}")
                else:
                    logger.debug(f"Request Body: {request.get_data(as_text=True)[:500]}")
            except Exception as e:
                logger.warning(f"Could not log request body: {e}")

        try:
            response = f(*args, **kwargs)

            duration = time.time() - start_time

            # Log response details
            if isinstance(response, tuple):
                status_code = response[1] if len(response) > 1 else 200
                response_data = response[0]
            else:
                status_code = 200
                response_data = response

            logger.debug(
                f"Response details:\n"
                f"  Status: {status_code}\n"
                f"  Duration: {duration:.3f}s\n"
                f"  Data: {str(response_data)[:500]}"
            )

            return response
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Request failed after {duration:.3f}s: {str(e)}\n"
                f"Traceback will be logged separately"
            )
            raise

    return decorated_function


def log_errors(f: Callable) -> Callable:
    """
    Decorator to log errors that occur during request processing.

    Args:
        f: The function to decorate

    Returns:
        Decorated function with error logging

    Example:
        >>> @log_errors
        ... def my_route():
        ...     raise ValueError("Something went wrong")
    """
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(
                f"Error in {request.method} {request.path}: {str(e)}",
                exc_info=True
            )
            raise

    return decorated_function


def log_performance(f: Callable) -> Callable:
    """
    Decorator to log performance metrics for requests.

    Args:
        f: The function to decorate

    Returns:
        Decorated function with performance logging

    Example:
        >>> @log_performance
        ... def my_route():
        ...     return {"message": "Hello"}
    """
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()

        try:
            response = f(*args, **kwargs)

            duration = time.time() - start_time

            # Log performance metrics
            logger.info(
                f"Performance: {request.method} {request.path} "
                f"completed in {duration:.3f}s"
            )

            # Log warning if request took too long (> 5 seconds)
            if duration > 5:
                logger.warning(
                    f"Slow request detected: {request.method} {request.path} "
                    f"took {duration:.3f}s"
                )

            return response
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Performance error: {request.method} {request.path} "
                f"failed after {duration:.3f}s: {str(e)}"
            )
            raise

    return decorated_function

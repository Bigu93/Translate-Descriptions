"""
Request handlers for authentication-related operations.
"""
from typing import Any, Tuple
from flask import request, jsonify
from app.infrastructure.logging.structured_logger import get_logger
from app.core.services.auth_service import AuthService
from app.core.services.token_service import TokenService
from app.handlers.error_handlers import handle_generic_error


logger = get_logger("auth_handlers")


class AuthHandlers:
    """
    Handlers for authentication-related API requests.
    """

    def __init__(self, auth_service: AuthService, token_service: TokenService):
        """
        Initialize auth handlers.

        Args:
            auth_service: Authentication service instance
            token_service: Token service instance
        """
        self.auth_service = auth_service
        self.token_service = token_service
        logger.info("AuthHandlers initialized")

    def authenticate(self) -> Tuple[Any, int]:
        """
        Handle authentication request.

        Returns:
            Tuple of (response_data, status_code)

        Example:
            >>> handlers = AuthHandlers(auth_service, token_service)
            >>> response, status = handlers.authenticate()
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify(error="Request body is required"), 400

            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                return jsonify(error="username and password are required"), 400

            # Authenticate user
            token = self.auth_service.authenticate(username, password)

            logger.info(f"User authenticated successfully: {username}")

            return jsonify({
                "token": token,
                "message": "Authentication successful"
            }), 200

        except Exception as e:
            logger.error(f"Error in authentication: {e}")
            return handle_generic_error(e)

    def validate_token(self) -> Tuple[Any, int]:
        """
        Handle token validation request.

        Returns:
            Tuple of (response_data, status_code)

        Example:
            >>> handlers = AuthHandlers(auth_service, token_service)
            >>> response, status = handlers.validate_token()
        """
        try:
            auth_header = request.headers.get("Authorization")

            if not auth_header:
                return jsonify(error="Missing Authorization header"), 401

            if not auth_header.startswith("Bearer "):
                return jsonify(error="Invalid Authorization header format"), 401

            token = auth_header[7:]  # Remove "Bearer " prefix

            # Validate token
            is_valid = self.token_service.validate_token(token)

            if is_valid:
                logger.info(f"Token validated successfully: {token[:10]}...")
                return jsonify({
                    "valid": True,
                    "message": "Token is valid"
                }), 200
            else:
                logger.warning(f"Invalid token: {token[:10]}...")
                return jsonify({
                    "valid": False,
                    "message": "Token is invalid or expired"
                }), 401

        except Exception as e:
            logger.error(f"Error validating token: {e}")
            return handle_generic_error(e)

    def refresh_token(self) -> Tuple[Any, int]:
        """
        Handle token refresh request.

        Returns:
            Tuple of (response_data, status_code)

        Example:
            >>> handlers = AuthHandlers(auth_service, token_service)
            >>> response, status = handlers.refresh_token()
        """
        try:
            auth_header = request.headers.get("Authorization")

            if not auth_header:
                return jsonify(error="Missing Authorization header"), 401

            if not auth_header.startswith("Bearer "):
                return jsonify(error="Invalid Authorization header format"), 401

            token = auth_header[7:]

            # Refresh token
            new_token = self.token_service.refresh_token(token)

            logger.info("Token refreshed successfully")

            return jsonify({
                "token": new_token,
                "message": "Token refreshed successfully"
            }), 200

        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            return handle_generic_error(e)

    def logout(self) -> Tuple[Any, int]:
        """
        Handle logout request.

        Returns:
            Tuple of (response_data, status_code)

        Example:
            >>> handlers = AuthHandlers(auth_service, token_service)
            >>> response, status = handlers.logout()
        """
        try:
            auth_header = request.headers.get("Authorization")

            if not auth_header:
                return jsonify(error="Missing Authorization header"), 401

            if not auth_header.startswith("Bearer "):
                return jsonify(error="Invalid Authorization header format"), 401

            token = auth_header[7:]

            # Revoke token
            self.token_service.revoke_token(token)

            logger.info("User logged out successfully")

            return jsonify({
                "message": "Logout successful"
            }), 200

        except Exception as e:
            logger.error(f"Error during logout: {e}")
            return handle_generic_error(e)

    def get_bearer_token(self) -> Tuple[Any, int]:
        """
        Handle bearer token retrieval request.

        Returns:
            Tuple of (response_data, status_code)

        Example:
            >>> handlers = AuthHandlers(auth_service, token_service)
            >>> response, status = handlers.get_bearer_token()
        """
        try:
            auth_header = request.headers.get("Authorization")

            if not auth_header:
                return jsonify(error="Missing Authorization header"), 401

            if not auth_header.startswith("Bearer "):
                return jsonify(error="Invalid Authorization header format"), 401

            token = auth_header[7:]

            # Get bearer token info
            bearer_info = self.auth_service.get_bearer_token(token)

            logger.info(f"Bearer token retrieved: {bearer_info[:10]}...")

            return jsonify({
                "bearer_token": bearer_info,
                "message": "Bearer token retrieved successfully"
            }), 200

        except Exception as e:
            logger.error(f"Error getting bearer token: {e}")
            return handle_generic_error(e)

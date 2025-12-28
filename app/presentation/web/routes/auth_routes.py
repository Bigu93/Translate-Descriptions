"""
Routes for authentication-related API endpoints.
"""
from flask import Blueprint
from app.presentation.web.handlers.auth_handlers import AuthHandlers
from app.presentation.web.middleware.logging_middleware import (
    log_request_response,
    log_performance,
)


def create_auth_routes(auth_handlers: AuthHandlers) -> Blueprint:
    """
    Create and configure authentication-related routes.

    Args:
        auth_handlers: Auth handlers instance

    Returns:
        Configured Flask Blueprint with auth routes

    Example:
        >>> handlers = AuthHandlers(auth_service, token_service)
        >>> routes = create_auth_routes(handlers)
        >>> app.register_blueprint(routes)
    """
    blueprint = Blueprint("auth", __name__, url_prefix="/api/auth")

    @blueprint.route("/authenticate", methods=["POST"])
    @log_request_response
    @log_performance
    def authenticate():
        """Authenticate user and return token."""
        return auth_handlers.authenticate()

    @blueprint.route("/validate", methods=["GET"])
    @log_request_response
    @log_performance
    def validate_token():
        """Validate authentication token."""
        return auth_handlers.validate_token()

    @blueprint.route("/refresh", methods=["POST"])
    @log_request_response
    @log_performance
    def refresh_token():
        """Refresh authentication token."""
        return auth_handlers.refresh_token()

    @blueprint.route("/logout", methods=["POST"])
    @log_request_response
    @log_performance
    def logout():
        """Logout user and revoke token."""
        return auth_handlers.logout()

    @blueprint.route("/bearer", methods=["GET"])
    @log_request_response
    @log_performance
    def get_bearer_token():
        """Get bearer token for API access."""
        return auth_handlers.get_bearer_token()

    return blueprint

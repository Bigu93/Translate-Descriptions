"""
Routes for authentication-related API endpoints.
"""
from flask import Blueprint
from app.presentation.web.middleware.logging_middleware import (
    log_request_response,
    log_performance,
)
from app.presentation.web.handlers.handler_registry import get_handler_registry


def create_auth_routes() -> Blueprint:
    """
    Create and configure authentication-related routes.

    Routes use the handler registry to get handlers lazily.
    Blueprints are registered at module load time, handlers are initialized on first request.

    Returns:
        Configured Flask Blueprint with auth routes

    Example:
        >>> routes = create_auth_routes()
        >>> app.register_blueprint(routes)
    """
    blueprint = Blueprint("auth", __name__, url_prefix="/api/auth")

    @blueprint.route("/authenticate", methods=["POST"])
    @log_request_response
    @log_performance
    def authenticate():
        """Authenticate user and return token."""
        registry = get_handler_registry()
        return registry.auth_handlers.authenticate()

    @blueprint.route("/validate", methods=["GET"])
    @log_request_response
    @log_performance
    def validate_token():
        """Validate authentication token."""
        registry = get_handler_registry()
        return registry.auth_handlers.validate_token()

    @blueprint.route("/refresh", methods=["POST"])
    @log_request_response
    @log_performance
    def refresh_token():
        """Refresh authentication token."""
        registry = get_handler_registry()
        return registry.auth_handlers.refresh_token()

    @blueprint.route("/logout", methods=["POST"])
    @log_request_response
    @log_performance
    def logout():
        """Logout user and revoke token."""
        registry = get_handler_registry()
        return registry.auth_handlers.logout()

    @blueprint.route("/bearer", methods=["GET"])
    @log_request_response
    @log_performance
    def get_bearer_token():
        """Get bearer token for API access."""
        registry = get_handler_registry()
        return registry.auth_handlers.get_bearer_token()

    return blueprint

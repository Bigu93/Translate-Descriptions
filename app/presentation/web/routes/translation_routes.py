"""
Routes for translation-related API endpoints.
"""
from flask import Blueprint
from app.presentation.web.middleware.logging_middleware import (
    log_request_response,
    log_performance,
)
from app.presentation.web.handlers.handler_registry import get_handler_registry


def create_translation_routes() -> Blueprint:
    """
    Create and configure translation-related routes.

    Routes use the handler registry to get handlers lazily.
    Blueprints are registered at module load time, handlers are initialized on first request.

    Returns:
        Configured Flask Blueprint with translation routes

    Example:
        >>> routes = create_translation_routes()
        >>> app.register_blueprint(routes)
    """
    blueprint = Blueprint("translations", __name__, url_prefix="/api/translations")

    @blueprint.route("/translate", methods=["POST"])
    @log_request_response
    @log_performance
    def translate():
        """Translate text to multiple languages."""
        registry = get_handler_registry()
        return registry.translation_handlers.translate()

    @blueprint.route("/generate-description", methods=["POST"])
    @log_request_response
    @log_performance
    def generate_description():
        """Generate product descriptions from product name."""
        registry = get_handler_registry()
        return registry.translation_handlers.generate_description()

    @blueprint.route("/rephrase-description", methods=["POST"])
    @log_request_response
    @log_performance
    def rephrase_description():
        """Rephrase existing descriptions."""
        registry = get_handler_registry()
        return registry.translation_handlers.rephrase_description()

    @blueprint.route("/translate-name", methods=["POST"])
    @log_request_response
    @log_performance
    def translate_product_name():
        """Translate product name to multiple languages."""
        registry = get_handler_registry()
        return registry.translation_handlers.translate_product_name()

    return blueprint

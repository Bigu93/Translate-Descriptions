"""
Routes for translation-related API endpoints.
"""
from flask import Blueprint
from app.presentation.web.handlers.translation_handlers import TranslationHandlers
from app.presentation.web.middleware.logging_middleware import (
    log_request_response,
    log_performance,
)


def create_translation_routes(translation_handlers: TranslationHandlers) -> Blueprint:
    """
    Create and configure translation-related routes.

    Args:
        translation_handlers: Translation handlers instance

    Returns:
        Configured Flask Blueprint with translation routes

    Example:
        >>> handlers = TranslationHandlers(translation_service)
        >>> routes = create_translation_routes(handlers)
        >>> app.register_blueprint(routes)
    """
    blueprint = Blueprint("translations", __name__, url_prefix="/api/translations")

    @blueprint.route("/translate", methods=["POST"])
    @log_request_response
    @log_performance
    def translate():
        """Translate text to multiple languages."""
        return translation_handlers.translate()

    @blueprint.route("/generate-description", methods=["POST"])
    @log_request_response
    @log_performance
    def generate_description():
        """Generate product descriptions from product name."""
        return translation_handlers.generate_description()

    @blueprint.route("/rephrase-description", methods=["POST"])
    @log_request_response
    @log_performance
    def rephrase_description():
        """Rephrase existing descriptions."""
        return translation_handlers.rephrase_description()

    @blueprint.route("/translate-name", methods=["POST"])
    @log_request_response
    @log_performance
    def translate_product_name():
        """Translate product name to multiple languages."""
        return translation_handlers.translate_product_name()

    return blueprint

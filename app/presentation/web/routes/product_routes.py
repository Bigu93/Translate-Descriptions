"""
Routes for product-related API endpoints.
"""
from flask import Blueprint, request
from app.presentation.web.middleware.logging_middleware import (
    log_request_response,
    log_performance,
)
from app.presentation.web.handlers.handler_registry import get_handler_registry


def create_product_routes() -> Blueprint:
    """
    Create and configure product-related routes.

    Routes use the handler registry to get handlers lazily.
    Blueprints are registered at module load time, handlers are initialized on first request.

    Returns:
        Configured Flask Blueprint with product routes

    Example:
        >>> routes = create_product_routes()
        >>> app.register_blueprint(routes)
    """
    blueprint = Blueprint("products", __name__, url_prefix="/api/products")

    @blueprint.route("/descriptions", methods=["GET"])
    @log_request_response
    @log_performance
    def get_product_description():
        """Get product descriptions by product ID and shop ID."""
        registry = get_handler_registry()
        return registry.product_handlers.get_product_description()

    @blueprint.route("/info/sizecode", methods=["POST"])
    @log_request_response
    @log_performance
    def get_product_info_with_sizecode():
        """Get product info by barcode/size code."""
        registry = get_handler_registry()
        return registry.product_handlers.get_product_info_with_sizecode()

    @blueprint.route("/full-info/sizecode", methods=["POST"])
    @log_request_response
    @log_performance
    def get_product_full_info_with_sizecode():
        """Get full product info by product ID and size code."""
        registry = get_handler_registry()
        return registry.product_handlers.get_product_full_info_with_sizecode()

    @blueprint.route("/full-info/ean", methods=["POST"])
    @log_request_response
    @log_performance
    def get_product_full_info_with_ean():
        """Get full product info by EAN code."""
        registry = get_handler_registry()
        return registry.product_handlers.get_product_full_info_with_ean()

    @blueprint.route("/images", methods=["POST"])
    @log_request_response
    @log_performance
    def get_product_images():
        """Get product images."""
        registry = get_handler_registry()
        return registry.product_handlers.get_product_images()

    @blueprint.route("/info", methods=["POST"])
    @log_request_response
    @log_performance
    def get_products_info():
        """Get products info with pagination."""
        registry = get_handler_registry()
        return registry.product_handlers.get_products_info()

    @blueprint.route("/descriptions", methods=["PUT"])
    @log_request_response
    @log_performance
    def set_product_description():
        """Set product descriptions."""
        registry = get_handler_registry()
        return registry.product_handlers.set_product_description()

    return blueprint

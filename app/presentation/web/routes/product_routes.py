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

    @blueprint.route("/descriptions", methods=["GET", "POST", "PUT"])
    @log_request_response
    @log_performance
    def handle_product_description():
        """Handle product descriptions (GET/POST for retrieve, PUT for update)."""
        registry = get_handler_registry()
        
        if request.method in ["GET", "POST"]:
            return registry.product_handlers.get_product_description()
        elif request.method == "PUT":
            return registry.product_handlers.set_product_description()

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
        """Get product images by product ID."""
        registry = get_handler_registry()
        return registry.product_handlers.get_product_images()

    @blueprint.route("/info", methods=["POST"])
    @log_request_response
    @log_performance
    def get_products_info():
        """Get products info with pagination."""
        registry = get_handler_registry()
        return registry.product_handlers.get_products_info()

    return blueprint

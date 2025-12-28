"""
Routes for product-related API endpoints.
"""
from flask import Blueprint, request
from app.presentation.web.handlers.product_handlers import ProductHandlers
from app.presentation.web.middleware.logging_middleware import (
    log_request_response,
    log_performance,
)


def create_product_routes(product_handlers: ProductHandlers) -> Blueprint:
    """
    Create and configure product-related routes.

    Args:
        product_handlers: Product handlers instance

    Returns:
        Configured Flask Blueprint with product routes

    Example:
        >>> handlers = ProductHandlers(products_client)
        >>> routes = create_product_routes(handlers)
        >>> app.register_blueprint(routes)
    """
    blueprint = Blueprint("products", __name__, url_prefix="/api/products")

    @blueprint.route("/descriptions", methods=["GET"])
    @log_request_response
    @log_performance
    def get_product_description():
        """Get product descriptions by product ID and shop ID."""
        return product_handlers.get_product_description()

    @blueprint.route("/info/sizecode", methods=["POST"])
    @log_request_response
    @log_performance
    def get_product_info_with_sizecode():
        """Get product info by barcode/size code."""
        return product_handlers.get_product_info_with_sizecode()

    @blueprint.route("/full-info/sizecode", methods=["POST"])
    @log_request_response
    @log_performance
    def get_product_full_info_with_sizecode():
        """Get full product info by product ID and size code."""
        return product_handlers.get_product_full_info_with_sizecode()

    @blueprint.route("/full-info/ean", methods=["POST"])
    @log_request_response
    @log_performance
    def get_product_full_info_with_ean():
        """Get full product info by EAN code."""
        return product_handlers.get_product_full_info_with_ean()

    @blueprint.route("/images", methods=["POST"])
    @log_request_response
    @log_performance
    def get_product_images():
        """Get product images."""
        return product_handlers.get_product_images()

    @blueprint.route("/info", methods=["POST"])
    @log_request_response
    @log_performance
    def get_products_info():
        """Get products info with pagination."""
        return product_handlers.get_products_info()

    @blueprint.route("/descriptions", methods=["PUT"])
    @log_request_response
    @log_performance
    def set_product_description():
        """Set product descriptions."""
        return product_handlers.set_product_description()

    return blueprint

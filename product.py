"""
Product data routes using new architecture.
"""
from flask import Blueprint, request
from app.core.services.product_service import ProductService
from app.factories.api_client_factory import create_products_client
from app.config.settings import get_base_url, get_client_username, get_client_secret
from app.infrastructure.logging.structured_logger import get_logger
from app.handlers.error_handlers import handle_generic_error
from urllib.parse import unquote


logger = get_logger("product")
product_bp = Blueprint("product", __name__)


def get_product_service() -> ProductService:
    """
    Get ProductService instance with dependency injection.

    Returns:
        Configured ProductService instance
    """
    base_url = get_base_url()
    client_username = get_client_username()
    client_secret = get_client_secret()
    products_client = create_products_client(base_url, client_username, client_secret)
    return ProductService(products_client)


def is_ean_code(product_id: str) -> bool:
    """
    Check if product_id is an EAN code.

    Args:
        product_id: The product ID to check

    Returns:
        True if product_id is an EAN code, False otherwise
    """
    return product_id.isdigit() and len(product_id) in {8, 12, 13, 14}


@product_bp.route("/<product_id>", methods=["GET"])
def get_product_data(product_id: str):
    """
    Get product data by product ID.

    Args:
        product_id: The product ID

    Returns:
        JSON response with product data
    """
    try:
        if not product_id:
            return {"error": "Product ID needs to be provided!"}, 400

        product_service = get_product_service()
        shop_id = request.args.get("shopid", default=0, type=int)
        lang_id = request.args.get("langid", default="pol", type=str).lower()
        lang_id = None if lang_id == "all" else lang_id

        fields_query = request.args.get("fields", default="productName", type=str)
        fields_list = (
            None if fields_query.lower() == "all" else unquote(fields_query).split(",")
        )

        data = product_service.get_product_description(
            product_id=product_id,
            shop_id=str(shop_id),
            lang=lang_id,
            fields=fields_list
        )

        logger.info(f"Retrieved product data for product_id: {product_id}")
        return data, 200

    except Exception as e:
        logger.error(f"Error getting product data: {e}")
        return handle_generic_error(e)


@product_bp.route("/<product_id>", methods=["POST"])
def set_product_data(product_id: str):
    """
    Set product data by product ID.

    Args:
        product_id: The product ID

    Returns:
        JSON response with update status
    """
    try:
        if not product_id:
            return {"error": "Product ID needs to be provided!"}, 400

        data = request.get_json()
        if not data:
            return {"error": "Empty payload!"}, 400

        if "params" not in data or "products" not in data["params"]:
            return {"error": "Unsupported JSON structure!"}, 400

        product_service = get_product_service()
        success = product_service.set_product_description(
            product_descriptions=data["params"]["products"]
        )

        if success:
            logger.info(f"Saved product data for product_id: {product_id}")
            return {"message": "Saved successfully!"}, 200
        else:
            return {"error": "Failed to save product data"}, 500

    except Exception as e:
        logger.error(f"Error setting product data: {e}")
        return handle_generic_error(e)


@product_bp.route("/full-info/<product_id>", methods=["GET"])
def get_full_product_info(product_id: str):
    """
    Get full product info by product ID.

    Args:
        product_id: The product ID

    Returns:
        JSON response with full product info
    """
    try:
        if not product_id:
            return {"error": "Product ID needs to be provided!"}, 400

        product_service = get_product_service()

        if is_ean_code(product_id):
            data = product_service.get_product_full_info_with_ean(product_id)
        else:
            parts = product_id.split("-")
            if len(parts) == 2:
                base_product_id, size_id = parts
                data = product_service.get_product_full_info_with_sizecode(
                    product_id=base_product_id,
                    size_code=size_id
                )
            else:
                return {"error": "Product ID with size code needs to be provided!"}, 400

        logger.info(f"Retrieved full product info for product_id: {product_id}")
        return data, 200

    except Exception as e:
        logger.error(f"Error getting full product info: {e}")
        return handle_generic_error(e)


@product_bp.route("/info/<product_ids>", methods=["GET"])
def get_products_info(product_ids: str):
    """
    Get products info by product IDs.

    Args:
        product_ids: Comma-separated product IDs

    Returns:
        JSON response with products info
    """
    try:
        if not product_ids:
            return {"error": "Product IDs need to be provided!"}, 400

        product_ids_list = product_ids.split(",")
        product_service = get_product_service()

        data = product_service.get_product_info_with_sizecode(product_ids_list)

        logger.info(f"Retrieved info for {len(product_ids_list)} products")
        return data, 200

    except Exception as e:
        logger.error(f"Error getting products info: {e}")
        return handle_generic_error(e)


@product_bp.route("/all", methods=["GET"])
def get_all_products():
    """
    Get all products with pagination.

    Returns:
        JSON response with products and pagination
    """
    try:
        page = request.args.get("page", default=0, type=int)
        limit = request.args.get("limit", default=50, type=int)

        if limit < 1 or limit > 100:
            return {"error": "limit must be between 1 and 100"}, 400

        product_service = get_product_service()

        # Get all product IDs (this would need to be implemented in ProductService)
        # For now, return empty list
        data = product_service.get_products_info(
            product_ids=[],
            page=page,
            limit=limit
        )

        logger.info(f"Retrieved all products for page {page}")
        return data, 200

    except Exception as e:
        logger.error(f"Error getting all products: {e}")
        return handle_generic_error(e)

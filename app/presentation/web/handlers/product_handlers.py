"""
Request handlers for product-related operations.
"""
from typing import Any, Dict, List, Optional, Tuple
from flask import request, jsonify
from app.infrastructure.logging.structured_logger import get_logger
from app.infrastructure.external_api.products_client import ProductsClient
from app.parsers.product_parser import (
    parse_product_data,
    parse_product_images,
    parse_product_info,
    parse_full_product_info,
    parse_full_products_info,
)
from app.handlers.error_handlers import handle_generic_error


logger = get_logger("product_handlers")


class ProductHandlers:
    """
    Handlers for product-related API requests.
    """

    def __init__(self, products_client: ProductsClient):
        """
        Initialize product handlers.

        Args:
            products_client: Products API client instance
        """
        self.products_client = products_client
        logger.info("ProductHandlers initialized")

    def get_product_description(self) -> Tuple[Any, int]:
        """
        Handle request to get product descriptions.
        
        Updated to support new API structure with product_id, shop_id, lang_id, fields.

        Returns:
            Tuple of (response_data, status_code)

        Example:
            >>> handlers = ProductHandlers(client)
            >>> response, status = handlers.get_product_description()
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify(error="Request body is required"), 400

            product_id = data.get("product_id")
            shop_id = data.get("shop_id")
            lang_id = data.get("lang_id", "all")
            fields = data.get("fields", "")

            if product_id is None or shop_id is None:
                return jsonify(error="product_id and shop_id are required"), 400

            # Parse fields into a list (handle both string and list input)
            if isinstance(fields, str):
                field_list = [f.strip() for f in fields.split(",") if f.strip()]
            elif isinstance(fields, list):
                field_list = [str(f).strip() for f in fields if str(f).strip()]
            else:
                field_list = []

            params = [product_id, shop_id]
            status_code, reason, response_data = self.products_client.get_product_description(params)

            parsed_data = parse_product_data(response_data)

            logger.info(f"Retrieved product description for product_id: {product_id}, lang_id: {lang_id}")
            return jsonify(parsed_data), status_code

        except Exception as e:
            logger.error(f"Error getting product description: {e}")
            return handle_generic_error(e)

    def get_product_info_with_sizecode(self) -> Tuple[Any, int]:
        """
        Handle request to get product info by barcode/size code.

        Returns:
            Tuple of (response_data, status_code)

        Example:
            >>> handlers = ProductHandlers(client)
            >>> response, status = handlers.get_product_info_with_sizecode()
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify(error="Request body is required"), 400

            barcodes = data.get("barcodes")
            if not barcodes or not isinstance(barcodes, list):
                return jsonify(error="barcodes list is required"), 400

            status_code, reason, response_data = self.products_client.get_product_info_with_sizecode(barcodes)

            parsed_data = parse_product_info(response_data)

            logger.info(f"Retrieved product info for {len(barcodes)} barcodes")
            return jsonify(parsed_data), status_code

        except Exception as e:
            logger.error(f"Error getting product info with sizecode: {e}")
            return handle_generic_error(e)

    def get_product_full_info_with_sizecode(self) -> Tuple[Any, int]:
        """
        Handle request to get full product info by product ID and size code.

        Returns:
            Tuple of (response_data, status_code)

        Example:
            >>> handlers = ProductHandlers(client)
            >>> response, status = handlers.get_product_full_info_with_sizecode()
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify(error="Request body is required"), 400

            product_id = data.get("product_id")
            size_code = data.get("size_code")

            if product_id is None or size_code is None:
                return jsonify(error="product_id and size_code are required"), 400

            params = [product_id, size_code]
            status_code, reason, response_data = self.products_client.get_product_full_info_with_sizecode(params)

            parsed_data = parse_full_product_info(response_data)

            logger.info(f"Retrieved full product info for product_id: {product_id}, size_code: {size_code}")
            return jsonify(parsed_data), status_code

        except Exception as e:
            logger.error(f"Error getting full product info with sizecode: {e}")
            return handle_generic_error(e)

    def get_product_full_info_with_ean(self) -> Tuple[Any, int]:
        """
        Handle request to get full product info by EAN code.

        Returns:
            Tuple of (response_data, status_code)

        Example:
            >>> handlers = ProductHandlers(client)
            >>> response, status = handlers.get_product_full_info_with_ean()
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify(error="Request body is required"), 400

            ean = data.get("ean")
            if not ean:
                return jsonify(error="ean is required"), 400

            status_code, reason, response_data = self.products_client.get_product_full_info_with_ean(ean)

            parsed_data = parse_full_product_info(response_data)

            logger.info(f"Retrieved full product info for EAN: {ean}")
            return jsonify(parsed_data), status_code

        except Exception as e:
            logger.error(f"Error getting full product info with EAN: {e}")
            return handle_generic_error(e)

    def get_product_images(self) -> Tuple[Any, int]:
        """
        Handle request to get product images.
        
        Updated to accept product_id in request body.

        Returns:
            Tuple of (response_data, status_code)

        Example:
            >>> handlers = ProductHandlers(client)
            >>> response, status = handlers.get_product_images()
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify(error="Request body is required"), 400

            product_id = data.get("product_id")
            if not product_id:
                return jsonify(error="product_id is required"), 400

            status_code, reason, response_data = self.products_client.get_product_images(data)

            parsed_data = parse_product_images(response_data)

            logger.info(f"Retrieved product images for product_id: {product_id}")
            return jsonify(parsed_data), status_code

        except Exception as e:
            logger.error(f"Error getting product images: {e}")
            return handle_generic_error(e)

    def get_products_info(self) -> Tuple[Any, int]:
        """
        Handle request to get products info with pagination.

        Returns:
            Tuple of (response_data, status_code)

        Example:
            >>> handlers = ProductHandlers(client)
            >>> response, status = handlers.get_products_info()
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify(error="Request body is required"), 400

            page = request.args.get("page", 0, type=int)
            base_url = f"{request.path}"

            status_code, reason, response_data = self.products_client.get_products_info(data)

            parsed_data = parse_full_products_info(response_data, base_url)

            logger.info(f"Retrieved products info for page {page}")
            return jsonify(parsed_data), status_code

        except Exception as e:
            logger.error(f"Error getting products info: {e}")
            return handle_generic_error(e)

    def set_product_description(self) -> Tuple[Any, int]:
        """
        Handle request to set product descriptions.

        Returns:
            Tuple of (response_data, status_code)

        Example:
            >>> handlers = ProductHandlers(client)
            >>> response, status = handlers.set_product_description()
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify(error="Request body is required"), 400

            status_code, reason, response_data = self.products_client.set_product_description(data)

            logger.info("Product description set successfully")
            return jsonify(response_data), status_code

        except Exception as e:
            logger.error(f"Error setting product description: {e}")
            return handle_generic_error(e)

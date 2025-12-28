"""
Service for managing product data operations.
"""
from typing import Dict, List, Optional, Tuple
from app.infrastructure.logging.structured_logger import get_logger
from app.infrastructure.external_api.products_client import ProductsClient
from app.parsers.product_parser import (
    parse_product_data,
    parse_product_images,
    parse_product_info,
    parse_full_product_info,
    parse_full_products_info,
)
from app.core.domain.exceptions import ExternalAPIError


logger = get_logger("product_service")


class ProductService:
    """
    Service for managing product data operations.
    """

    def __init__(self, products_client: ProductsClient):
        """
        Initialize product service.

        Args:
            products_client: Products API client instance
        """
        self.products_client = products_client
        logger.info("ProductService initialized")

    def get_product_description(
        self,
        product_id: str,
        shop_id: str,
        lang: Optional[str] = None,
        fields: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Get product descriptions by product ID and shop ID.

        Args:
            product_id: The product ID
            shop_id: The shop ID
            lang: Optional language filter
            fields: Optional list of fields to include

        Returns:
            List of parsed product descriptions

        Raises:
            ExternalAPIError: If API request fails

        Example:
            >>> service = ProductService(client)
            >>> descriptions = service.get_product_description(
            ...     product_id="123",
            ...     shop_id="456",
            ...     lang="eng"
            ... )
        """
        try:
            params = [product_id, shop_id]
            status_code, reason, response_data = self.products_client.get_product_description(params)

            parsed_data = parse_product_data(response_data, lang=lang, fields=fields)

            logger.info(f"Retrieved product description for product_id: {product_id}")
            return parsed_data

        except Exception as e:
            logger.error(f"Error getting product description: {e}")
            raise ExternalAPIError(f"Failed to get product description: {e}") from e

    def get_product_info_with_sizecode(
        self,
        barcodes: List[str]
    ) -> List[Dict]:
        """
        Get product info by barcode/size code.

        Args:
            barcodes: List of product barcodes/size codes

        Returns:
            List of parsed product information

        Raises:
            ExternalAPIError: If API request fails

        Example:
            >>> service = ProductService(client)
            >>> info = service.get_product_info_with_sizecode(
            ...     barcodes=["123456", "789012"]
            ... )
        """
        try:
            status_code, reason, response_data = self.products_client.get_product_info_with_sizecode(barcodes)

            parsed_data = parse_product_info(response_data)

            logger.info(f"Retrieved product info for {len(barcodes)} barcodes")
            return parsed_data

        except Exception as e:
            logger.error(f"Error getting product info with sizecode: {e}")
            raise ExternalAPIError(f"Failed to get product info: {e}") from e

    def get_product_full_info_with_sizecode(
        self,
        product_id: str,
        size_code: str
    ) -> List[Dict]:
        """
        Get full product info by product ID and size code.

        Args:
            product_id: The product ID
            size_code: The size code

        Returns:
            List of parsed full product information

        Raises:
            ExternalAPIError: If API request fails

        Example:
            >>> service = ProductService(client)
            >>> info = service.get_product_full_info_with_sizecode(
            ...     product_id="123",
            ...     size_code="S"
            ... )
        """
        try:
            params = [product_id, size_code]
            status_code, reason, response_data = self.products_client.get_product_full_info_with_sizecode(params)

            parsed_data = parse_full_product_info(response_data)

            logger.info(f"Retrieved full product info for product_id: {product_id}, size_code: {size_code}")
            return parsed_data

        except Exception as e:
            logger.error(f"Error getting full product info with sizecode: {e}")
            raise ExternalAPIError(f"Failed to get full product info: {e}") from e

    def get_product_full_info_with_ean(
        self,
        ean: str
    ) -> List[Dict]:
        """
        Get full product info by EAN code.

        Args:
            ean: The EAN code

        Returns:
            List of parsed full product information

        Raises:
            ExternalAPIError: If API request fails

        Example:
            >>> service = ProductService(client)
            >>> info = service.get_product_full_info_with_ean(
            ...     ean="1234567890123"
            ... )
        """
        try:
            status_code, reason, response_data = self.products_client.get_product_full_info_with_ean(ean)

            parsed_data = parse_full_product_info(response_data)

            logger.info(f"Retrieved full product info for EAN: {ean}")
            return parsed_data

        except Exception as e:
            logger.error(f"Error getting full product info with EAN: {e}")
            raise ExternalAPIError(f"Failed to get full product info: {e}") from e

    def get_product_images(
        self,
        product_ids: List[str]
    ) -> List[Dict]:
        """
        Get product images.

        Args:
            product_ids: List of product IDs

        Returns:
            List of product images

        Raises:
            ExternalAPIError: If API request fails

        Example:
            >>> service = ProductService(client)
            >>> images = service.get_product_images(
            ...     product_ids=["123", "456"]
            ... )
        """
        try:
            data = {"productIds": product_ids}
            status_code, reason, response_data = self.products_client.get_product_images(data)

            parsed_data = parse_product_images(response_data)

            logger.info(f"Retrieved images for {len(product_ids)} products")
            return parsed_data

        except Exception as e:
            logger.error(f"Error getting product images: {e}")
            raise ExternalAPIError(f"Failed to get product images: {e}") from e

    def get_products_info(
        self,
        product_ids: List[str],
        page: int = 0,
        limit: int = 10
    ) -> Dict:
        """
        Get products info with pagination.

        Args:
            product_ids: List of product IDs
            page: Page number (default: 0)
            limit: Results per page (default: 10)

        Returns:
            Dictionary containing data and pagination info

        Raises:
            ExternalAPIError: If API request fails

        Example:
            >>> service = ProductService(client)
            >>> result = service.get_products_info(
            ...     product_ids=["123", "456"],
            ...     page=0,
            ...     limit=10
            ... )
            >>> result["data"]
            [...]
            >>> result["pagination"]["current_page"]
            0
        """
        try:
            data = {
                "productIds": product_ids,
                "resultsPage": page,
                "resultsLimit": limit
            }
            status_code, reason, response_data = self.products_client.get_products_info(data)

            base_url = f"/api/products/info"
            parsed_data = parse_full_products_info(response_data, base_url)

            logger.info(f"Retrieved products info for page {page}")
            return parsed_data

        except Exception as e:
            logger.error(f"Error getting products info: {e}")
            raise ExternalAPIError(f"Failed to get products info: {e}") from e

    def set_product_description(
        self,
        product_descriptions: List[Dict]
    ) -> bool:
        """
        Set product descriptions.

        Args:
            product_descriptions: List of product description data

        Returns:
            True if successful

        Raises:
            ExternalAPIError: If API request fails

        Example:
            >>> service = ProductService(client)
            >>> success = service.set_product_description([
            ...     {
            ...         "productId": "123",
            ...         "productDescriptionsLangData": [
            ...             {"langId": "eng", "name": "Product Name"}
            ...         ]
            ...     }
            ... ])
        """
        try:
            data = {"productDescriptionsLangData": product_descriptions}
            status_code, reason, response_data = self.products_client.set_product_description(data)

            logger.info(f"Set product descriptions for {len(product_descriptions)} products")
            return True

        except Exception as e:
            logger.error(f"Error setting product description: {e}")
            raise ExternalAPIError(f"Failed to set product description: {e}") from e

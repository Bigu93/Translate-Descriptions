"""
Client for interacting with the Products API.
"""
from typing import Tuple, Dict, Any, Optional, List, Callable
from app.infrastructure.logging.structured_logger import get_logger
from app.infrastructure.external_api.base_client import BaseClient, APIRequestError, APIResponseError
from app.infrastructure.external_api.auth_client import AuthClient
from app.core.domain.exceptions import ValidationError, ExternalAPIError


class ProductsClient:
    """
    Client for making requests to the Products API.
    """

    def __init__(
        self,
        hostname: str,
        auth_token: str,
        version: str = "v3",
        ssl_verify: bool = True,
        auth_client: Optional[AuthClient] = None,
        api_key: str = "",
        logger: Optional[object] = None,
    ):
        """
        Constructor for ProductsClient class.

        Args:
            hostname: API base URL
            auth_token: Authentication token
            version: API version (default: "v3")
            ssl_verify: Whether to verify SSL certificates (default: True)
            logger: Optional logger instance (default: creates "api" logger)

        Example:
            >>> client = ProductsClient(
            ...     hostname="https://api.example.com",
            ...     auth_token="token123"
            ... )
        """
        self._base_client = BaseClient(
            hostname=hostname,
            auth_token=auth_token,
            version=version,
            ssl_verify=ssl_verify,
            api_key=api_key,
            logger=logger,
        )
        self.logger = logger if logger else get_logger("api")
        self._auth_client = auth_client

    def _ensure_token(self, force_refresh: bool = False) -> None:
        """Ensure the BaseClient has a fresh Authorization header.

        This app creates a singleton `ProductsClient` in [`app.initialize_services()`](Translate-Descriptions/app.py:55)
        and keeps it for the whole process lifetime; external API tokens expire.
        """
        if not self._auth_client:
            return
        token = self._auth_client.get_token(force_refresh=force_refresh)
        self._base_client.set_bearer_token(token)

    def _call_with_optional_refresh(self, call: Callable[[], Tuple[int, str, Dict[str, Any]]]) -> Tuple[int, str, Dict[str, Any]]:
        """Run a BaseClient call; on 401 refresh token once and retry."""
        self._ensure_token(force_refresh=False)
        try:
            return call()
        except APIResponseError as e:
            if e.status_code == 401 and self._auth_client is not None:
                self.logger.warning(
                    "External API returned 401. Refreshing token and retrying once.",
                    url=getattr(e, "url", ""),
                )
                # Force re-auth (token could be revoked/expired server-side).
                self._ensure_token(force_refresh=True)
                return call()
            raise

    @staticmethod
    def _to_external_api_error(prefix: str, e: Exception) -> ExternalAPIError:
        if isinstance(e, APIResponseError):
            return ExternalAPIError(
                f"{prefix}: {str(e)}",
                status_code=getattr(e, "status_code", None),
                response=getattr(e, "response_text", None),
            )
        return ExternalAPIError(f"{prefix}: {str(e)}")

    def get_product_description(self, params: List[Any]) -> Tuple[int, str, Dict[str, Any]]:
        """
        Get product descriptions by product ID and shop ID.

        Args:
            params: List containing [product_id, shop_id]

        Returns:
            Tuple of (status_code, reason, response_data)

        Raises:
            ValidationError: If params are invalid
            APIRequestError: If the request fails
            APIResponseError: If the response is invalid

        Example:
            >>> client.get_product_description(["123", "456"])
            (200, 'OK', {'results': [...]})
        """
        if not isinstance(params, (list, tuple)) or len(params) < 2:
            raise ValidationError(
                "Invalid params: expected a list or tuple with at least two elements"
            )

        endpoint = f"products/descriptions?type=id&ids={params[0]}&shopId={params[1]}"
        try:
            return self._call_with_optional_refresh(lambda: self._base_client.get(endpoint=endpoint))
        except (APIRequestError, APIResponseError) as e:
            self.logger.error(f"Failed to get product description: {e}")
            raise self._to_external_api_error("Failed to get product description", e) from e

    def get_product_info_with_sizecode(self, params: List[str]) -> Tuple[int, str, Dict[str, Any]]:
        """
        Get product info by barcode/size code.

        Args:
            params: List of product indices/barcodes

        Returns:
            Tuple of (status_code, reason, response_data)

        Raises:
            ValidationError: If params are invalid
            APIRequestError: If the request fails
            APIResponseError: If the response is invalid

        Example:
            >>> client.get_product_info_with_sizecode(["123", "456"])
            (200, 'OK', {'results': [...]})
        """
        if not isinstance(params, (list, tuple)) or not params:
            raise ValidationError(
                "Invalid params: expected a non-empty list or tuple"
            )

        product_ids = ",".join(str(p) for p in params)
        endpoint = f"products/SKUbyBarcode?productIndices={product_ids}"
        try:
            return self._call_with_optional_refresh(lambda: self._base_client.get(endpoint=endpoint))
        except (APIRequestError, APIResponseError) as e:
            self.logger.error(f"Failed to get product info with size code: {e}")
            raise self._to_external_api_error("Failed to get product info with size code", e) from e

    def get_product_full_info_with_sizecode(self, params: List[Any]) -> Tuple[int, str, Dict[str, Any]]:
        """
        Get full product info by product ID and size code.

        Args:
            params: List containing [product_id, size_code]

        Returns:
            Tuple of (status_code, reason, response_data)

        Raises:
            ValidationError: If params are invalid
            APIRequestError: If the request fails
            APIResponseError: If the response is invalid

        Example:
            >>> client.get_product_full_info_with_sizecode(["123", "S"])
            (200, 'OK', {'results': [...]})
        """
        if not isinstance(params, (list, tuple)) or len(params) < 2:
            raise ValidationError(
                "Invalid params: expected a list or tuple with at least two elements"
            )

        endpoint = f"products/products?productIds={params[0]}-{params[1]}"
        try:
            return self._call_with_optional_refresh(lambda: self._base_client.get(endpoint=endpoint))
        except (APIRequestError, APIResponseError) as e:
            self.logger.error(f"Failed to get full product info with sizecode: {e}")
            raise self._to_external_api_error("Failed to get full product info with sizecode", e) from e

    def get_product_full_info_with_ean(self, params: str) -> Tuple[int, str, Dict[str, Any]]:
        """
        Get full product info by EAN code.

        Args:
            params: EAN code string

        Returns:
            Tuple of (status_code, reason, response_data)

        Raises:
            ValidationError: If params are invalid
            APIRequestError: If the request fails
            APIResponseError: If the response is invalid

        Example:
            >>> client.get_product_full_info_with_ean("1234567890123")
            (200, 'OK', {'results': [...]})
        """
        if not params or not isinstance(params, str):
            raise ValidationError("Invalid params: expected a non-empty string")

        endpoint = f"products/products?productIds={params}"
        try:
            return self._call_with_optional_refresh(lambda: self._base_client.get(endpoint=endpoint))
        except (APIRequestError, APIResponseError) as e:
            self.logger.error(f"Failed to get full product info with EAN: {e}")
            raise self._to_external_api_error("Failed to get full product info with EAN", e) from e

    def get_product_images(self, data: Dict[str, Any]) -> Tuple[int, str, Dict[str, Any]]:
        """
        Get product images.

        For IdoSell v6, images are fetched via `products/products/search` with
        `returnElements: ["pictures"]`.

        Args:
            data: Dictionary containing product IDs

        Returns:
            Tuple of (status_code, reason, response_data)

        Raises:
            ValidationError: If data is invalid
            APIRequestError: If the request fails
            APIResponseError: If the response is invalid

        Example (preferred):
            >>> client.get_product_images({"productIds": ["123"]})
            (200, 'OK', {'results': [...]})
        """
        if not isinstance(data, dict) or not data:
            raise ValidationError("data must be a non-empty dictionary.")

        # Accept simplified input from the app layer and convert it to the IdoSell v6
        # search payload that returns pictures.
        payload: Dict[str, Any] = data
        if "params" not in payload:
            product_ids = payload.get("productIds")
            if isinstance(product_ids, (list, tuple)) and product_ids:
                product_params = [{"productId": int(pid)} for pid in product_ids]
            elif "product_id" in payload:
                product_params = [{"productId": int(payload["product_id"])}]
            else:
                product_params = []

            payload = {
                "params": {
                    "returnElements": ["pictures"],
                    "productParams": product_params,
                }
            }

        endpoint = "products/products/search"
        try:
            return self._call_with_optional_refresh(
                lambda: self._base_client.post(endpoint=endpoint, data=payload)
            )
        except (APIRequestError, APIResponseError) as e:
            self.logger.error(f"Failed to get product images: {e}")
            raise self._to_external_api_error("Failed to get product images", e) from e

    def get_products_info(self, data: Dict[str, Any]) -> Tuple[int, str, Dict[str, Any]]:
        """
        Get products info.

        Args:
            data: Dictionary containing product IDs and other filters

        Returns:
            Tuple of (status_code, reason, response_data)

        Raises:
            ValidationError: If data is invalid
            APIRequestError: If the request fails
            APIResponseError: If the response is invalid

        Example:
            >>> client.get_products_info({"productIds": ["123", "456"]})
            (200, 'OK', {'results': [...]})
        """
        if not isinstance(data, dict) or not data:
            raise ValidationError("data must be a non-empty dictionary.")

        endpoint = "products/products/get"
        try:
            return self._call_with_optional_refresh(lambda: self._base_client.post(endpoint=endpoint, data=data))
        except (APIRequestError, APIResponseError) as e:
            self.logger.error(f"Failed to get products info: {e}")
            raise self._to_external_api_error("Failed to get products info", e) from e

    def set_product_description(self, data: Dict[str, Any]) -> Tuple[int, str, Dict[str, Any]]:
        """
        Set product descriptions.

        Args:
            data: Dictionary containing product description data

        Returns:
            Tuple of (status_code, reason, response_data)

        Raises:
            ValidationError: If data is invalid
            APIRequestError: If the request fails
            APIResponseError: If the response is invalid

        Example:
            >>> client.set_product_description({
            ...     "productDescriptionsLangData": [
            ...         {"langId": "eng", "name": "Product Name"}
            ...     ]
            ... })
            (200, 'OK', {'results': [...]})
        """
        if not isinstance(data, dict) or not data:
            raise ValidationError("data must be a non-empty dictionary.")

        endpoint = "products/descriptions"
        try:
            return self._call_with_optional_refresh(lambda: self._base_client.put(endpoint=endpoint, data=data))
        except (APIRequestError, APIResponseError) as e:
            self.logger.error(f"Failed to set product description: {e}")
            raise self._to_external_api_error("Failed to set product description", e) from e

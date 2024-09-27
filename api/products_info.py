from logging_config import get_logger
from api.base_client import BaseClient, APIRequestError, APIResponseError


class ProductApi:

    def __init__(
        self,
        hostname: str,
        auth_token: str,
        version: str = "v3",
        ssl_verify: bool = True,
        logger: get_logger = None,
    ):
        self._base_client = BaseClient(
            hostname, auth_token, version, ssl_verify, logger
        )
        self.logger = logger if logger else get_logger("api")

    def get_product_description(self, params):
        if not isinstance(params, (list, tuple)) or len(params) < 2:
            raise ValueError(
                "Invalid params: expected a list or tuple with at least two elements"
            )

        endpoint = f"products/descriptions?type=id&ids={params[0]}&shopId={params[1]}"
        try:
            return self._base_client.get(endpoint=endpoint)
        except (APIRequestError, APIResponseError) as e:
            self._logger.error(f"Failed to get product description: {e}")
            raise

    def get_product_info_with_sizecode(self, params):
        product_ids = ",".join(params)
        endpoint = f"products/SKUbyBarcode?productIndices={product_ids}"
        try:
            return self._base_client.get(endpoint=endpoint)
        except (APIRequestError, APIResponseError) as e:
            self._logger.error(f"Failed to get product info with size code: {e}")
            raise
        return result

    def get_product_full_info_with_sizecode(self, params):
        if not isinstance(params, (list, tuple)) or len(params) < 2:
            raise ValueError(
                "Invalid params: expected a list or tuple with at least two elements"
            )

        endpoint = f"products/products?productIds={params[0]}-{params[1]}"
        try:
            return self._base_client.get(endpoint=endpoint)
        except (APIRequestError, APIResponseError) as e:
            self._logger.error(f"Failed to get full product info with sizecode: {e}")
            raise

    def get_product_full_info_with_ean(self, params):
        if not params:
            raise ValueError("Invalid params: expected a string")

        endpoint = f"products/products?productIds={params}"
        try:
            return self._base_client.get(endpoint=endpoint)
        except (APIRequestError, APIResponseError) as e:
            self._logger.error(f"Failed to get full product info with EAN: {e}")
            raise

    def get_product_images(self, data: dict):
        if not isinstance(data, dict) or not data:
            raise ValueError("data must be a non-empty dictionary.")

        endpoint = "products/products/get"
        try:
            return self._base_client.post(endpoint=endpoint, data=data)
        except (APIRequestError, APIResponseError) as e:
            self._logger.error(f"Failed to get product images: {e}")
            raise

    def get_products_info(self, data: dict):
        if not isinstance(data, dict) or not data:
            raise ValueError("data must be a non-empty dictionary.")

        endpoint = "products/products/get"
        try:
            return self._base_client.post(endpoint=endpoint, data=data)
        except (APIRequestError, APIResponseError) as e:
            self._logger.error(f"Failed to get products info: {e}")
            raise

    def set_product_description(self, data: dict):
        if not isinstance(data, dict) or not data:
            raise ValueError("data must be a non-empty dictionary.")

        endpoint = "products/descriptions"
        try:
            return self._base_client.put(endpoint=endpoint, data=data)
        except (APIRequestError, APIResponseError) as e:
            self._logger.error(f"Failed to set product description: {e}")
            raise

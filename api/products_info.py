import logging
from api.base_client import BaseClient


class ProductApi:
    def __init__(
        self,
        hostname: str,
        auth_token: str,
        ver: str,
        ssl_verify: bool = True,
        logger: logging.Logger = None,
    ):
        self._base_client = BaseClient(hostname, auth_token, ver, ssl_verify, logger)

    def get_product_description(self, params):
        if not isinstance(params, (list, tuple)) or len(params) < 2:
            raise ValueError(
                "Invalid params: expected a list or tuple with at least two elements"
            )

        endpoint = f"products/descriptions?type=id&ids={params[0]}&shopId={params[1]}"
        result = self._base_client.get(endpoint=endpoint)
        return result

    def get_product_info_with_sizecode(self, params):
        if not isinstance(params, (list, tuple)) or len(params) < 2:
            raise ValueError(
                "Invalid params: expected a list or tuple with at least two elements"
            )

        endpoint = f"products/SKUbyBarcode?productIndices={params[0]}-{params[1]}"
        result = self._base_client.get(endpoint=endpoint)
        return result

    def get_product_full_info_with_sizecode(self, params):
        if not isinstance(params, (list, tuple)) or len(params) < 2:
            raise ValueError(
                "Invalid params: expected a list or tuple with at least two elements"
            )

        endpoint = f"products/products?productIds={params[0]}-{params[1]}"
        result = self._base_client.get(endpoint=endpoint)
        return result

    def get_product_images(self, data):
        if not data:
            raise Exception("You need to provide data for a product")

        endpoint = "products/products/get"
        payload = data
        result = self._base_client.post(endpoint=endpoint, data=payload)
        return result

    def set_product_description(self, data):
        endpoint = "products/descriptions"
        payload = data
        result = self._base_client.put(endpoint=endpoint, data=payload)
        return result

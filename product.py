import logging
from base_client import BaseClient


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

    def set_product_description(self, data):
        if not isinstance(data, (list, tuple)) or len(data) < 3:
            raise ValueError(
                "Invalid params: expected a list or tuple with at least two elements"
            )
        endpoint = "products/descriptions"
        payload = ""
        result = self._base_client.put(endpoint=endpoint, data=data)

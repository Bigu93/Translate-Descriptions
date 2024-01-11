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
        result = self._base_client.get(
            endpoint="products/descriptions?type=id&ids={params[0]}&shopId={params[1]}",
            ep_params=None,
        )
        return result

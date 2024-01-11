import logging
from base_client import BaseClient


class ProductApi:
    def __init__(
        self,
        hostname: str,
        auth_token: str,
        ver: str = "v2",
        ssl_verify: bool = True,
        logger: logging.Logger = None,
    ):
        self._base_client = BaseClient(hostname, auth_token, ver, ssl_verify, logger)

    def get_product_description(self, id, shop_id):
        result = self._base_client.post(
            endpoint="products/descriptions?type=id&ids={id}&shopId={shop_id}"
        )
        return result

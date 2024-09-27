import requests
import requests.packages
from logging_config import get_logger
from json import JSONDecodeError

DEFAULT_TIMEOUT = 10  # seconds


class APIRequestError(Exception):
    """Exception raised for errors during the API request."""

    pass


class APIResponseError(Exception):
    """Exception raised for invalid API responses."""

    pass


class BaseClient:

    def __init__(
        self,
        hostname: str,
        auth_token: str = "",
        version: str = "v3",
        ssl_verify: bool = True,
        logger: get_logger = None,
    ):
        """
        Constructor for BaseClient class
        :param hostname: website url
        :param auth_token: authentication token
        :param version: v3
        :param ssl_verify: Normally set to True, but if having SSL/TLS cert validation issues, can turn off with False
        :param logger: (optional) If your app has a logger, pass it in here.
        """
        self.logger = logger if logger else get_logger("api")
        self.url = f"{hostname.rstrip('/')}/{version}/"
        self.auth_token = auth_token
        self._ssl_verify = ssl_verify
        self.session = requests.Session()
        self.session.verify = ssl_verify
        if not ssl_verify:
            requests.packages.urllib3.disable_warnings()

        # Set default headers
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.auth_token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    def get(self, endpoint: str, ep_params: dict = None):
        return self._send_request("GET", endpoint, params=ep_params)

    def post(self, endpoint: str, ep_params: dict = None, data: dict = None):
        return self._send_request("POST", endpoint, params=ep_params, json=data)

    def put(self, endpoint: str, ep_params: dict = None, data: dict = None):
        return self._send_request("PUT", endpoint, params=ep_params, json=data)

    def delete(self, endpoint: str, ep_params: dict = None):
        return self._send_request("DELETE", endpoint, params=ep_params)

    def _send_request(
        self,
        method: str,
        endpoint: str,
        params: dict = None,
        json: dict = None,
    ):
        full_url = self.url + endpoint
        self.logger.debug(
            f"Preparing {method} request to URL: {full_url} with params: {params} and data: {json}"
        )

        try:
            response = self.session.request(
                method=method,
                url=full_url,
                params=params,
                json=json,
                timeout=DEFAULT_TIMEOUT,
            )
            self.logger.debug(
                f"Received response with status code: {response.status_code}"
            )
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request exception: {e}")
            raise APIRequestError(f"Request failed: {e}") from e

        if not 200 <= response.status_code < 300:
            self.logger.error(
                f"Unexpected status code: {response.status_code} - {response.text}"
            )
            raise APIResponseError(
                f"Unexpected status code: {response.status_code} - {response.text}"
            )

        try:
            data_out = response.json()
        except (ValueError, JSONDecodeError) as e:
            self.logger.error(msg=log_line_post.format(False, None, e))
            raise Exception("Bad JSON in response") from e

        try:
            data_out = response.json()
            self.logger.debug(f"Response JSON: {data_out}")
            return (response.status_code, response.reason, data_out)
        except JSONDecodeError as e:
            self.logger.error(
                f"JSON decode error: {e} - Response text: {response.text}"
            )
            raise APIResponseError("Failed to decode JSON response.") from e

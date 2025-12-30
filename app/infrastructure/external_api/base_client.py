"""
Base HTTP client for external API communication.
"""
import requests
import requests.packages
from json import JSONDecodeError
from typing import Optional, Tuple, Dict, Any
from app.infrastructure.logging.structured_logger import get_logger
from app.shared.decorators.retry_decorator import retry
from app.core.domain.exceptions import ExternalAPIError


DEFAULT_TIMEOUT = 10  # seconds


class APIRequestError(Exception):
    """Exception raised for errors during the API request."""

    pass


class APIResponseError(Exception):
    """Exception raised for invalid API responses."""

    pass


class BaseClient:
    """
    Base HTTP client for making API requests with retry logic and comprehensive logging.
    """

    def __init__(
        self,
        hostname: str,
        auth_token: str = "",
        version: str = "v3",
        ssl_verify: bool = True,
        logger: Optional[object] = None,
    ):
        """
        Constructor for BaseClient class.

        Args:
            hostname: Website URL
            auth_token: Authentication token
            version: API version (default: "v3")
            ssl_verify: Whether to verify SSL certificates (default: True)
            logger: Optional logger instance (default: creates "api" logger)

        Example:
            >>> client = BaseClient(
            ...     hostname="https://api.example.com",
            ...     auth_token="token123",
            ...     version="v3"
            ... )
        """
        self.logger = logger if logger else get_logger("api")
        self.url = f"{hostname.rstrip('/')}/{version}/"
        self.auth_token = auth_token
        self._ssl_verify = ssl_verify
        self.session = requests.Session()
        self.session.verify = ssl_verify

        if not ssl_verify:
            requests.packages.urllib3.disable_warnings()

        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.auth_token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

        self.logger.debug(f"BaseClient initialized for {self.url}")

    def get(self, endpoint: str, ep_params: Optional[Dict[str, Any]] = None) -> Tuple[int, str, Dict[str, Any]]:
        """
        Send a GET request.

        Args:
            endpoint: API endpoint
            ep_params: Optional query parameters

        Returns:
            Tuple of (status_code, reason, response_data)

        Example:
            >>> client.get("products/descriptions", {"ids": "123"})
            (200, 'OK', {'results': [...]})
        """
        return self._send_request("GET", endpoint, params=ep_params)

    def post(
        self,
        endpoint: str,
        ep_params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Tuple[int, str, Dict[str, Any]]:
        """
        Send a POST request.

        Args:
            endpoint: API endpoint
            ep_params: Optional query parameters
            data: Optional JSON data to send

        Returns:
            Tuple of (status_code, reason, response_data)

        Example:
            >>> client.post("products/descriptions", data={"name": "Product"})
            (200, 'OK', {'results': [...]})
        """
        return self._send_request("POST", endpoint, params=ep_params, json=data)

    def put(
        self,
        endpoint: str,
        ep_params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Tuple[int, str, Dict[str, Any]]:
        """
        Send a PUT request.

        Args:
            endpoint: API endpoint
            ep_params: Optional query parameters
            data: Optional JSON data to send

        Returns:
            Tuple of (status_code, reason, response_data)

        Example:
            >>> client.put("products/descriptions", data={"name": "Updated Product"})
            (200, 'OK', {'results': [...]})
        """
        return self._send_request("PUT", endpoint, params=ep_params, json=data)

    def delete(self, endpoint: str, ep_params: Optional[Dict[str, Any]] = None) -> Tuple[int, str, Dict[str, Any]]:
        """
        Send a DELETE request.

        Args:
            endpoint: API endpoint
            ep_params: Optional query parameters

        Returns:
            Tuple of (status_code, reason, response_data)

        Example:
            >>> client.delete("products/descriptions", {"ids": "123"})
            (200, 'OK', {'results': [...]})
        """
        return self._send_request("DELETE", endpoint, params=ep_params)

    @retry(max_attempts=3, delay=1, backoff_factor=2, exceptions=(requests.exceptions.RequestException,))
    def _send_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Tuple[int, str, Dict[str, Any]]:
        """
        Send an HTTP request with retry logic and comprehensive logging.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            params: Optional query parameters
            json: Optional JSON data to send

        Returns:
            Tuple of (status_code, reason, response_data)

        Raises:
            APIRequestError: If the request fails
            APIResponseError: If the response is invalid
        """
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
            self.logger.debug(f"Response JSON: {data_out}")
            return (response.status_code, response.reason, data_out)
        except (ValueError, JSONDecodeError) as e:
            self.logger.error(
                f"JSON decode error: {e} - Response text: {response.text[:500]}"
            )
            raise APIResponseError("Failed to decode JSON response.") from e

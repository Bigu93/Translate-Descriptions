"""
Base HTTP client for external API communication.
"""
import time
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
    """Exception raised for invalid API responses.

    Carries HTTP status code and a truncated response body (when available)
    so callers can implement smarter recovery (e.g. refresh token on 401).
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_text: str = "",
        url: str = "",
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text
        self.url = url


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
        api_key: str = "",
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

        # Default headers.
        # For IdoSell v6 the API commonly uses `X-API-KEY` auth.
        # For older flows this client may use Bearer auth.
        self.session.headers.update({"Accept": "application/json", "Content-Type": "application/json"})

        if api_key:
            self.session.headers["X-API-KEY"] = api_key

        if self.auth_token:
            self.session.headers["Authorization"] = f"Bearer {self.auth_token}"

        self.logger.debug(f"BaseClient initialized for {self.url}")

    def set_bearer_token(self, token: str) -> None:
        """Update the Authorization header used for subsequent requests."""
        self.auth_token = token or ""
        if self.auth_token:
            self.session.headers["Authorization"] = f"Bearer {self.auth_token}"
        else:
            # Avoid sending empty Authorization headers.
            self.session.headers.pop("Authorization", None)

    @staticmethod
    def _obfuscate_token(token: str) -> str:
        if not token:
            return "<empty>"
        if len(token) <= 10:
            return "****"
        return f"{token[:4]}****{token[-3:]}"

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

        start = time.monotonic()

        # Helpful diagnostics when dealing with auth/token expiry issues.
        try:
            auth_header = self.session.headers.get("Authorization", "")
            token = ""
            if auth_header.lower().startswith("bearer "):
                token = auth_header.split(" ", 1)[1]
            self.logger.debug(
                f"Authorization header present: {bool(auth_header)}; bearer token: {self._obfuscate_token(token)}"
            )
        except Exception:
            # Never fail the request due to logging/diagnostics.
            pass

        try:
            response = self.session.request(
                method=method,
                url=full_url,
                params=params,
                json=json,
                timeout=DEFAULT_TIMEOUT,
            )

            duration_ms = int((time.monotonic() - start) * 1000)
            json_keys = list(json.keys()) if isinstance(json, dict) else None
            # NOTE: StructuredLogger stores context in `extra=...`, but the configured
            # formatter prints only `%(message)s`. Put key diagnostics in the message.
            self.logger.info(
                "External API request completed: "
                f"method={method} url={full_url} status_code={response.status_code} "
                f"duration_ms={duration_ms} timeout_s={DEFAULT_TIMEOUT} "
                f"params_present={bool(params)} json_keys={json_keys}"
            )
            self.logger.debug(
                f"Received response with status code: {response.status_code}"
            )
        except requests.exceptions.RequestException as e:
            duration_ms = int((time.monotonic() - start) * 1000)
            json_keys = list(json.keys()) if isinstance(json, dict) else None
            self.logger.error(
                "External API request exception: "
                f"method={method} url={full_url} duration_ms={duration_ms} "
                f"timeout_s={DEFAULT_TIMEOUT} exception_type={type(e).__name__} "
                f"params_present={bool(params)} json_keys={json_keys} error={e}"
            )
            raise APIRequestError(f"Request failed: {e}") from e

        if not 200 <= response.status_code < 300:
            response_text = (response.text or "")
            truncated = response_text[:500]
            www_auth = response.headers.get("WWW-Authenticate")
            if www_auth:
                self.logger.error(
                    f"Unexpected status code: {response.status_code} - {truncated} (WWW-Authenticate: {www_auth})"
                )
            else:
                self.logger.error(
                    f"Unexpected status code: {response.status_code} - {truncated}"
                )
            raise APIResponseError(
                f"Unexpected status code: {response.status_code} - {truncated}",
                status_code=response.status_code,
                response_text=truncated,
                url=full_url,
            )

        try:
            data_out = response.json()
            self.logger.debug(f"Response JSON: {data_out}")
            return (response.status_code, response.reason, data_out)
        except (ValueError, JSONDecodeError) as e:
            self.logger.error(
                f"JSON decode error: {e} - Response text: {response.text[:500]}"
            )
            raise APIResponseError(
                "Failed to decode JSON response.",
                status_code=response.status_code,
                response_text=(response.text or "")[:500],
                url=full_url,
            ) from e

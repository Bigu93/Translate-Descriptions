"""
Client for handling API authentication.
"""
import requests
import time
import base64
from typing import Optional
from app.infrastructure.logging.structured_logger import get_logger
from app.shared.decorators.retry_decorator import retry
from app.core.domain.exceptions import AuthenticationError


class AuthClient:
    """
    Client for handling API authentication with token caching.
    """

    def __init__(
        self,
        base_url: str,
        client_username: str,
        client_secret: str,
        auth_endpoint: str = "authorize/1/authorize/accessToken",
        buffer_time: int = 60,
        logger: Optional[object] = None,
    ):
        """
        Constructor for AuthClient class.

        Args:
            base_url: URL for API gateway
            client_username: Panel API username
            client_secret: Panel API secret
            auth_endpoint: Endpoint for authentication
            buffer_time: Buffer time in seconds before token expires (default: 60)
            logger: Optional logger instance (default: creates "auth" logger)

        Example:
            >>> client = AuthClient(
            ...     base_url="https://api.example.com/v3",
            ...     client_username="user",
            ...     client_secret="secret"
            ... )
        """
        self.logger = logger if logger else get_logger("auth")
        self.encoded_credentials = self.encode_credentials(
            client_username, client_secret
        )
        self.base_url = base_url.rstrip("/")
        self.auth_endpoint = auth_endpoint
        self.buffer_time = buffer_time
        self.access_token = None
        self.token_expires = 0

    @staticmethod
    def encode_credentials(client_username: str, client_secret: str) -> str:
        """
        Encode client credentials using Base64.

        Args:
            client_username: API username
            client_secret: API secret

        Returns:
            Base64 encoded credentials string

        Example:
            >>> AuthClient.encode_credentials("user", "secret")
            'dXNlcjpzZWNyZXQ='
        """
        credentials = f"{client_username}:{client_secret}"
        return base64.b64encode(credentials.encode()).decode()

    def get_basic_auth_header(self) -> str:
        """
        Get the Basic Authentication header value.

        Returns:
            Basic auth header string

        Example:
            >>> client.get_basic_auth_header()
            'Basic dXNlcjpzZWNyZXQ='
        """
        return f"Basic {self.encoded_credentials}"

    def is_token_valid(self) -> bool:
        """
        Check if the current access token is valid.

        Returns:
            True if token is valid and not expired, False otherwise

        Example:
            >>> client.is_token_valid()
            True
        """
        return self.access_token and time.time() < (
            self.token_expires - self.buffer_time
        )

    def get_token(self) -> str:
        """
        Get a valid access token, authenticating if necessary.

        Returns:
            Valid access token string

        Raises:
            AuthenticationError: If authentication fails

        Example:
            >>> token = client.get_token()
            >>> print(token)
            'eyJhbGciOiJIUzI1NiIs...'
        """
        if not self.is_token_valid():
            self.authenticate()
        return self.access_token

    @retry(max_attempts=3, delay=1, backoff_factor=2, exceptions=(requests.RequestException,))
    def authenticate(self) -> None:
        """
        Authenticate with the API and store the access token.

        Raises:
            AuthenticationError: If authentication fails

        Example:
            >>> client.authenticate()
            >>> print(client.access_token)
            'eyJhbGciOiJIUzI1NiIs...'
        """
        url = self._build_auth_url()
        payload = {"grant_type": "client_credentials", "scope": ["api-pa"]}
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": self.get_basic_auth_header(),
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            self.access_token = data["access_token"]
            self.token_expires = time.time() + int(data["expires_in"])
            self.logger.info("Authentication successful.")
        except requests.RequestException as e:
            self.logger.error(f"Error in authentication request: {e}")
            self.access_token = None
            self.token_expires = 0
            raise AuthenticationError(
                f"API Authentication Error: {e.response.status_code} - {e.response.text}"
            ) from e
        except KeyError as e:
            self.logger.error(f"Unexpected response structure: {e}")
            raise AuthenticationError(
                "Invalid response structure during authentication."
            ) from e

    def _build_auth_url(self) -> str:
        """
        Build the authentication URL.

        Returns:
            Full authentication URL

        Example:
            >>> client._build_auth_url()
            'https://api.example.com/authorize/1/authorize/accessToken'
        """
        gateway_url = self.base_url.rsplit('/', 1)[0]
        return f"{gateway_url}/{self.auth_endpoint}"

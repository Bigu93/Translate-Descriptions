import requests
import time
import base64
from logging_config import get_logger

logger = get_logger("auth")


class AuthenticationError(Exception):
    """Custom exception for authentication failures."""

    pass


class Auth:
    BUFFER_TIME = 60  # seconds

    def __init__(
        self,
        client_username,
        client_secret,
        base_url,
        auth_endpoint="authorize/1/authorize/accessToken",
        logger=None,
    ):
        """
        Constructor for Auth class
        :param client_username: panel api username
        :param client_secret: panel api secret
        :param base_url: url for api gateway
        :param api_version: version of api
        :param auth_endpoint: Endpoint for authentication
        :param logger: Logger instance (optional), default to "auth" logger if not provided
        """
        self.logger = logger if logger else get_logger("auth")
        self.encoded_credentials = self.encode_credentials(
            client_username, client_secret
        )
        self.base_url = base_url.rstrip("/")
        self.auth_endpoint = auth_endpoint
        self.access_token = None
        self.token_expires = 0

    @staticmethod
    def encode_credentials(client_username, client_secret):
        credentials = f"{client_username}:{client_secret}"
        return base64.b64encode(credentials.encode()).decode()

    def get_basic_auth_header(self):
        return f"Basic {self.encoded_credentials}"

    def is_token_valid(self):
        return self.access_token and time.time() < (
            self.token_expires - self.BUFFER_TIME
        )

    def get_token(self):
        if not self.is_token_valid():
            self.authenticate()
        return self.access_token

    def authenticate(self):
        url = f"{self.base_url.rsplit('/', 1)[0]}/{self.auth_endpoint}"
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
            )

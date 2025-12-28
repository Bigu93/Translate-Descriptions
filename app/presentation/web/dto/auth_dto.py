"""
Data Transfer Objects for authentication-related requests and responses.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class AuthenticationRequest:
    """DTO for authentication requests."""
    username: str
    password: str

    def validate(self) -> Optional[str]:
        """
        Validate authentication request.

        Returns:
            Error message if validation fails, None otherwise
        """
        if not self.username:
            return "username is required"

        if not self.password:
            return "password is required"

        if len(self.username) < 3:
            return "username must be at least 3 characters"

        if len(self.password) < 6:
            return "password must be at least 6 characters"

        return None


@dataclass
class AuthenticationResponse:
    """DTO for authentication responses."""
    token: str
    message: str

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "token": self.token,
            "message": self.message
        }


@dataclass
class TokenValidationResponse:
    """DTO for token validation responses."""
    valid: bool
    message: str

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "valid": self.valid,
            "message": self.message
        }


@dataclass
class TokenRefreshResponse:
    """DTO for token refresh responses."""
    token: str
    message: str

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "token": self.token,
            "message": self.message
        }


@dataclass
class LogoutResponse:
    """DTO for logout responses."""
    message: str

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "message": self.message
        }


@dataclass
class BearerTokenResponse:
    """DTO for bearer token responses."""
    bearer_token: str
    message: str

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "bearer_token": self.bearer_token,
            "message": self.message
        }

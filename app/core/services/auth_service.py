"""
Authentication service for Translate-Descriptions application.

This module implements business logic for bearer token authentication,
using Repository Pattern for data access.
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional
from app.core.domain.interfaces import IAuthService
from app.core.domain.models import AuthToken
from app.core.domain.exceptions import DatabaseError
from app.infrastructure.database.bearer_repository import BearerRepository
from app.core.domain.interfaces import ILogger


class AuthService(IAuthService):
    """Service for managing bearer authentication tokens.
    
    Implements IAuthService interface using BearerRepository.
    Provides token generation, validation, and revocation.
    """
    
    def __init__(
        self,
        bearer_repository: BearerRepository,
        logger: ILogger,
        token_expiry_days: int = 30
    ):
        """Initialize auth service.
        
        Args:
            bearer_repository: Bearer token repository
            logger: Logger instance
            token_expiry_days: Token expiry time in days (default: 30)
        """
        self._repository = bearer_repository
        self._logger = logger
        self._token_expiry_days = token_expiry_days
    
    def generate_auth_token(self) -> AuthToken:
        """Generate a bearer authentication token.
        
        Creates a URL-safe token with 30-day expiry.
        
        Returns:
            AuthToken entity with token string and expiry time
            
        Raises:
            DatabaseError: If token cannot be created
        """
        token_str = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(days=self._token_expiry_days)
        
        success = self._repository.create(token_str, expires_at)
        
        if not success:
            error_msg = "Failed to generate auth token"
            if self._logger:
                self._logger.error(error_msg)
            raise DatabaseError(error_msg)
        
        token = AuthToken(token=token_str, expires_at=expires_at)
        
        if self._logger:
            self._logger.info(
                f"Generated new auth token: {token.obfuscate()}",
                expires_at=expires_at.isoformat()
            )
        
        return token
    
    def revoke_auth_token(self, token: str) -> bool:
        """Revoke a bearer authentication token.
        
        Args:
            token: Token string to revoke
            
        Returns:
            True if successful, False otherwise
        """
        success = self._repository.delete_by_token(token)
        
        if self._logger:
            if success:
                self._logger.info(f"Revoked auth token: {self._obfuscate(token)}")
            else:
                self._logger.warning(f"Token not found for revocation: {self._obfuscate(token)}")
        
        return success
    
    def validate_auth_token(self, token: str) -> bool:
        """Validate a bearer authentication token.
        
        Checks if token exists in database and has not expired.
        
        Args:
            token: Token string to validate
            
        Returns:
            True if token is valid and not expired, False otherwise
        """
        token_data = self._repository.find_valid_token(token)
        
        is_valid = token_data is not None
        
        if self._logger:
            if is_valid:
                self._logger.debug(f"Auth token validated: {self._obfuscate(token)}")
            else:
                self._logger.warning(f"Invalid or expired auth token: {self._obfuscate(token)}")
        
        return is_valid
    
    def _obfuscate(self, token: str) -> str:
        """Obfuscate token for logging.
        
        Shows only first and last character for security.
        
        Args:
            token: Token string to obfuscate
            
        Returns:
            Obfuscated token string (e.g., "a****z")
        """
        if len(token) <= 8:
            return "****"
        return f"{token[:1]}****{token[-1:]}"

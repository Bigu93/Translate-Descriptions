"""
Token service for Translate-Descriptions application.

This module implements business logic for temporary API token management,
using Repository Pattern for data access and Observer Pattern for events.
"""

import secrets
from datetime import datetime, timedelta
from typing import List
from app.core.domain.interfaces import ITokenService
from app.core.domain.models import Token
from app.core.domain.exceptions import DatabaseError
from app.infrastructure.database.token_repository import TokenRepository
from app.core.domain.interfaces import ILogger


class TokenService(ITokenService):
    """Service for managing API tokens.
    
    Implements ITokenService interface using TokenRepository.
    Provides token generation, validation, and cleanup operations.
    """
    
    def __init__(
        self,
        token_repository: TokenRepository,
        logger: ILogger,
        token_expiry_hours: int = 1
    ):
        """Initialize token service.
        
        Args:
            token_repository: Token repository for data access
            logger: Logger instance
            token_expiry_hours: Token expiry time in hours (default: 1)
        """
        self._repository = token_repository
        self._logger = logger
        self._token_expiry_hours = token_expiry_hours
    
    def generate_token(self) -> Token:
        """Generate a new API token.
        
        Creates a cryptographically secure token with expiry time.
        
        Returns:
            Token entity with token string and expiry time
            
        Raises:
            DatabaseError: If token cannot be created
        """
        token_str = secrets.token_hex(16)
        expires_at = datetime.now() + timedelta(hours=self._token_expiry_hours)
        
        success = self._repository.create(token_str, expires_at)
        
        if not success:
            error_msg = "Failed to generate token"
            if self._logger:
                self._logger.error(error_msg)
            raise DatabaseError(error_msg)
        
        token = Token(token=token_str, expires_at=expires_at)
        
        if self._logger:
            self._logger.info(
                f"Generated new token: {token.obfuscate()}",
                expires_at=expires_at.isoformat()
            )
        
        return token
    
    def validate_token(self, token: str) -> bool:
        """Validate a token.
        
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
                self._logger.debug(f"Token validated: {self._obfuscate(token)}")
            else:
                self._logger.warning(
                    f"Invalid or expired token: {self._obfuscate(token)}"
                )
        
        return is_valid
    
    def cleanup_expired_tokens(self) -> int:
        """Remove expired tokens from database.
        
        Returns:
            Number of tokens removed
        """
        deleted_count = self._repository.delete_expired_tokens()
        
        if self._logger:
            if deleted_count > 0:
                self._logger.info(f"Cleaned up {deleted_count} expired tokens")
            else:
                self._logger.info("No expired tokens to clean up")
        
        return deleted_count
    
    def get_all_tokens(self) -> List[Token]:
        """Get all tokens.
        
        Returns:
            List of all Token entities
        """
        token_data_list = self._repository.find_all()
        
        tokens = [
            Token(
                token=td['token'],
                expires_at=td['expires_at']
            )
            for td in token_data_list
        ]
        
        if self._logger:
            self._logger.info(f"Found {len(tokens)} tokens in database")
        
        return tokens
    
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

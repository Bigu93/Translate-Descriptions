"""
Bearer token repository for database operations.

This module implements repository pattern for bearer token management,
removing duplicate database code from auth_bearer.py.
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from app.infrastructure.database.base_repository import BaseRepository
from app.core.domain.models import AuthToken
from app.core.domain.exceptions import DatabaseError


class BearerRepository(BaseRepository):
    """Repository for bearer token data access.
    
    Implements Repository Pattern for bearer token CRUD operations.
    Removes duplicate database code from auth_bearer.py.
    """
    
    def create(self, token: str, expires_at: datetime) -> bool:
        """Create a new bearer token.
        
        Args:
            token: Token string value
            expires_at: Token expiry datetime
            
        Returns:
            True if successful, False otherwise
        """
        query = "INSERT INTO bearer (token, expires_at) VALUES (%s, %s)"
        try:
            result = self._execute_query(query, (token, expires_at), fetch=False)
            if self._logger:
                self._logger.info(
                    f"Created bearer token: {self._obfuscate_token(token)}",
                    expires_at=expires_at.isoformat()
                )
            return result > 0
        except DatabaseError:
            return False
    
    def find_valid_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Find a valid (non-expired) bearer token.
        
        Args:
            token: Token string to find
            
        Returns:
            Token data dictionary or None if not found/expired
        """
        query = """
            SELECT token, expires_at 
            FROM bearer 
            WHERE token = %s AND expires_at > NOW()
        """
        results = self._execute_query(query, (token,))
        
        if results and len(results) > 0:
            return results[0]
        return None
    
    def delete_by_token(self, token: str) -> bool:
        """Delete bearer token by token value.
        
        Args:
            token: Token string to delete
            
        Returns:
            True if successful, False otherwise
        """
        query = "DELETE FROM bearer WHERE token = %s"
        result = self._execute_query(query, (token,), fetch=False)
        if self._logger:
            self._logger.info(
                f"Deleted bearer token: {self._obfuscate_token(token)}"
            )
        return result > 0
    
    def find_all(self) -> List[Dict[str, Any]]:
        """Find all bearer tokens.
        
        Returns:
            List of all bearer token data dictionaries
        """
        query = "SELECT token, expires_at FROM bearer ORDER BY expires_at"
        return self._execute_query(query)
    
    def find_by_id(self, id: Any) -> Optional[Dict[str, Any]]:
        """Find entity by ID.
        
        Bearer tokens don't have numeric IDs, use find_valid_token instead.
        
        Raises:
            NotImplementedError: Always raised
        """
        raise NotImplementedError("Use find_valid_token instead")
    
    def save(self, entity: Dict[str, Any]) -> bool:
        """Save entity.
        
        Delegates to create method.
        
        Args:
            entity: Entity dictionary with 'token' and 'expires_at'
            
        Returns:
            True if successful, False otherwise
        """
        return self.create(entity['token'], entity['expires_at'])
    
    def delete(self, id: Any) -> bool:
        """Delete entity by ID.
        
        Delegates to delete_by_token method.
        
        Args:
            id: Token string to delete
            
        Returns:
            True if successful, False otherwise
        """
        return self.delete_by_token(id)
    
    def _obfuscate_token(self, token: str) -> str:
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

"""
Base repository for database operations.

This module provides an abstract base class for all repositories,
implementing common database operations and connection management.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from app.infrastructure.database.connection_pool import ConnectionPool
from app.core.domain.exceptions import DatabaseError
from app.core.domain.interfaces import ILogger


class BaseRepository(ABC):
    """Base repository with common database operations.
    
    Implements Template Method Pattern for database operations.
    All repositories inherit from this class for consistent behavior.
    """
    
    def __init__(self, connection_pool: ConnectionPool, logger: ILogger = None):
        """Initialize repository with connection pool.
        
        Args:
            connection_pool: Database connection pool
            logger: Logger instance (optional)
        """
        self._pool = connection_pool
        self._logger = logger
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections.
        
        Yields a connection from the pool and ensures
        it's returned after use, even if an exception occurs.
        
        Yields:
            MySQL connection object
        """
        connection = self._pool.get_connection()
        try:
            yield connection
        finally:
            self._pool.return_connection(connection)
    
    @abstractmethod
    def find_by_id(self, id: Any) -> Optional[Dict[str, Any]]:
        """Find entity by ID.
        
        Args:
            id: Entity identifier
            
        Returns:
            Entity data dictionary or None if not found
        """
        pass
    
    @abstractmethod
    def find_all(self) -> List[Dict[str, Any]]:
        """Find all entities.
        
        Returns:
            List of entity data dictionaries
        """
        pass
    
    @abstractmethod
    def save(self, entity: Dict[str, Any]) -> bool:
        """Save entity.
        
        Args:
            entity: Entity data dictionary
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def delete(self, id: Any) -> bool:
        """Delete entity by ID.
        
        Args:
            id: Entity identifier
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    def _execute_query(
        self,
        query: str,
        params: tuple = None,
        fetch: bool = True
    ) -> Any:
        """Execute a query with connection management.
        
        Template method for executing SQL queries with automatic
        connection handling and error processing.
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
            fetch: Whether to fetch results (default: True)
            
        Returns:
            Query results if fetch=True, rowcount if fetch=False
            
        Raises:
            DatabaseError: If query execution fails
        """
        with self._get_connection() as conn:
            try:
                cursor = conn.cursor(buffered=True)
                
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                conn.commit()
                
                if fetch:
                    # Return results as list of dictionaries
                    cursor.fetchall()
                    results = cursor.fetchall()
                    # Convert to list of dicts if not already
                    if results and isinstance(results[0], tuple):
                        columns = [desc[0] for desc in cursor.description]
                        results = [dict(zip(columns, row)) for row in results]
                    return results
                else:
                    return cursor.rowcount
                    
            except Exception as e:
                conn.rollback()
                error_msg = f"Query execution failed: {e}"
                if self._logger:
                    self._logger.error(error_msg, query=query, params=params)
                raise DatabaseError(error_msg) from e

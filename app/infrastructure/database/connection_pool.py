"""
Database connection pool for Translate-Descriptions application.

This module implements a connection pool for MySQL connections following
the Object Pool design pattern. It provides efficient connection management
with health checks and proper resource cleanup.
"""

import threading
import queue
import mysql.connector
from mysql.connector import Error
from typing import Optional
from app.core.domain.exceptions import DatabaseError
from app.core.domain.interfaces import ILogger


class ConnectionPool:
    """MySQL connection pool with configurable size.
    
    Implements Object Pool Pattern for efficient database connection management.
    Features:
    - Configurable pool size and overflow
    - Connection health checks
    - Thread-safe operations
    - Proper resource cleanup
    - Pool statistics
    """
    
    def __init__(
        self,
        host: str,
        database: str,
        user: str,
        password: str,
        pool_size: int = 5,
        max_overflow: int = 10,
        pool_timeout: int = 30,
        logger: ILogger = None
    ):
        """Initialize connection pool.
        
        Args:
            host: Database host
            database: Database name
            user: Database user
            password: Database password
            pool_size: Base pool size
            max_overflow: Maximum additional connections beyond pool size
            pool_timeout: Timeout in seconds for getting connection
            logger: Logger instance
        """
        self._host = host
        self._database = database
        self._user = user
        self._password = password
        self._pool_size = pool_size
        self._max_overflow = max_overflow
        self._pool_timeout = pool_timeout
        self._logger = logger
        self._pool = queue.Queue(maxsize=pool_size + max_overflow)
        self._active_connections = 0
        self._lock = threading.Lock()
        
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize the connection pool with base connections."""
        for _ in range(self._pool_size):
            try:
                connection = self._create_connection()
                self._pool.put(connection)
            except DatabaseError:
                pass
        
        if self._logger:
            self._logger.info(
                f"Initialized connection pool with {self._pool.qsize()} connections"
            )
    
    def _create_connection(self) -> mysql.connector.MySQLConnection:
        """Create a new database connection.
        
        Returns:
            MySQL connection object
            
        Raises:
            DatabaseError: If connection cannot be established
        """
        try:
            connection = mysql.connector.connect(
                host=self._host,
                database=self._database,
                user=self._user,
                password=self._password,
                pool_name="translate_descriptions_pool",
                pool_size=1,
                autocommit=False
            )
            if self._logger:
                self._logger.debug("Created new database connection")
            return connection
        except Error as e:
            if self._logger:
                self._logger.error(f"Failed to create database connection: {e}")
            raise DatabaseError(f"Failed to create database connection: {e}") from e
    
    def _is_connection_valid(
        self, connection: mysql.connector.MySQLConnection
    ) -> bool:
        """Check if connection is still valid.
        
        Args:
            connection: Connection to check
            
        Returns:
            True if connection is valid, False otherwise
        """
        try:
            return connection.is_connected()
        except Error:
            return False
    
    def get_connection(self) -> mysql.connector.MySQLConnection:
        """Get a connection from the pool.
        
        Will create a new connection if pool is exhausted
        and under max_overflow limit.
        
        Returns:
            MySQL connection object
            
        Raises:
            DatabaseError: If pool is exhausted
        """
        try:
            connection = self._pool.get(timeout=self._pool_timeout)
            
            if not self._is_connection_valid(connection):
                connection.close()
                connection = self._create_connection()
            
            with self._lock:
                self._active_connections += 1
            
            if self._logger:
                self._logger.debug(
                    f"Retrieved connection from pool. Active: {self._active_connections}"
                )
            return connection
            
        except queue.Empty:
            with self._lock:
                if self._active_connections < self._pool_size + self._max_overflow:
                    connection = self._create_connection()
                    self._active_connections += 1
                    if self._logger:
                        self._logger.debug(
                            f"Created new overflow connection. Active: {self._active_connections}"
                        )
                    return connection
            
            if self._logger:
                self._logger.error("Connection pool exhausted")
            raise DatabaseError("Connection pool exhausted")
    
    def return_connection(self, connection: mysql.connector.MySQLConnection):
        """Return a connection to the pool.
        
        Closes invalid connections and returns valid ones to pool.
        
        Args:
            connection: Connection to return
        """
        try:
            if self._is_connection_valid(connection):
                self._pool.put(connection, timeout=1)
                if self._logger:
                    self._logger.debug("Returned connection to pool")
            else:
                connection.close()
                with self._lock:
                    self._active_connections -= 1
                if self._logger:
                    self._logger.debug("Returned invalid connection, closed it")
            
            with self._lock:
                self._active_connections -= 1
            
            if self._logger:
                self._logger.debug(
                    f"Returned connection to pool. Active: {self._active_connections}"
                )
        except queue.Full:
            connection.close()
            with self._lock:
                self._active_connections -= 1
            if self._logger:
                self._logger.debug("Pool full, closed connection")
    
    def close_all(self):
        """Close all connections in the pool.
        
        Should be called during application shutdown.
        """
        while not self._pool.empty():
            try:
                connection = self._pool.get_nowait()
                connection.close()
            except queue.Empty:
                break
        
        if self._logger:
            self._logger.info("Closed all connections in pool")
    
    def get_pool_stats(self) -> dict:
        """Get pool statistics.
        
        Returns:
            Dictionary with pool statistics
        """
        return {
            "pool_size": self._pool_size,
            "max_overflow": self._max_overflow,
            "active_connections": self._active_connections,
            "available_connections": self._pool.qsize()
        }


_connection_pool_instance: Optional[ConnectionPool] = None


def get_connection_pool() -> ConnectionPool:
    """Get connection pool instance (Singleton).
    
    Creates connection pool with configuration from Settings.
    Returns the same instance on subsequent calls.
    
    Returns:
        ConnectionPool instance
        
    Raises:
        DatabaseError: If connection pool cannot be created
    """
    global _connection_pool_instance
    
    if _connection_pool_instance is None:
        from app.config.settings import Settings
        from app.infrastructure.logging.structured_logger import get_logger
        
        settings = Settings.get_instance()
        logger = get_logger("database")
        
        _connection_pool_instance = ConnectionPool(
            host=settings.database.host,
            database=settings.database.database,
            user=settings.database.user,
            password=settings.database.password,
            pool_size=settings.database.pool_size,
            max_overflow=settings.database.max_overflow,
            pool_timeout=settings.database.pool_timeout,
            logger=logger
        )
        
        logger.info(
            f"Created connection pool with pool_size={settings.database.pool_size}, "
            f"max_overflow={settings.database.max_overflow}"
        )
    
    return _connection_pool_instance

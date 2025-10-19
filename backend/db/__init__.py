"""
REIMS Database Module

Provides async PostgreSQL connection management and query execution.
"""

from .connection import (
    # Core functions
    init_db,
    close_db,
    get_connection,
    get_pool,
    health_check,
    
    # Query functions
    execute,
    fetch_one,
    fetch_all,
    fetch_val,
    
    # Exceptions
    DatabaseError,
    ConnectionError,
    QueryError,
    PoolNotInitializedError,
    
    # Configuration
    DatabaseConfig,
)

__all__ = [
    # Core functions
    'init_db',
    'close_db',
    'get_connection',
    'get_pool',
    'health_check',
    
    # Query functions
    'execute',
    'fetch_one',
    'fetch_all',
    'fetch_val',
    
    # Exceptions
    'DatabaseError',
    'ConnectionError',
    'QueryError',
    'PoolNotInitializedError',
    
    # Configuration
    'DatabaseConfig',
]

















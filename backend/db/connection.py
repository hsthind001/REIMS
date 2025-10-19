"""
REIMS Database Connection Module

Async PostgreSQL connection pool using asyncpg.
Provides connection management, query execution, and health checks.

Author: REIMS Development Team
Date: October 12, 2025
"""

import os
import logging
import asyncpg
from typing import Any, List, Optional, Union
from contextlib import asynccontextmanager
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


# Custom Exceptions
class DatabaseError(Exception):
    """Base exception for database errors"""
    pass


class ConnectionError(DatabaseError):
    """Raised when connection to database fails"""
    pass


class QueryError(DatabaseError):
    """Raised when query execution fails"""
    pass


class PoolNotInitializedError(DatabaseError):
    """Raised when attempting to use pool before initialization"""
    pass


# Global connection pool
_connection_pool: Optional[asyncpg.Pool] = None


# Database Configuration
class DatabaseConfig:
    """Database configuration from environment variables"""
    
    HOST = os.getenv('DATABASE_HOST', 'localhost')
    PORT = int(os.getenv('DATABASE_PORT', '5432'))
    DATABASE = os.getenv('DATABASE_NAME', 'reims')
    USER = os.getenv('DATABASE_USER', 'postgres')
    PASSWORD = os.getenv('DATABASE_PASSWORD', '')
    
    # Connection Pool Settings
    MIN_POOL_SIZE = 10
    MAX_POOL_SIZE = 20
    CONNECTION_TIMEOUT = 30.0  # seconds
    COMMAND_TIMEOUT = 5.0      # seconds
    
    # SSL Configuration
    SSL_MODE = 'require' if os.getenv('ENVIRONMENT', 'development') == 'production' else 'prefer'
    
    @classmethod
    def get_dsn(cls) -> str:
        """Generate PostgreSQL DSN (Data Source Name)"""
        return f"postgresql://{cls.USER}:{cls.PASSWORD}@{cls.HOST}:{cls.PORT}/{cls.DATABASE}"
    
    @classmethod
    def log_config(cls) -> None:
        """Log current configuration (without password)"""
        logger.info(f"Database Configuration:")
        logger.info(f"  Host: {cls.HOST}")
        logger.info(f"  Port: {cls.PORT}")
        logger.info(f"  Database: {cls.DATABASE}")
        logger.info(f"  User: {cls.USER}")
        logger.info(f"  SSL Mode: {cls.SSL_MODE}")
        logger.info(f"  Pool: min={cls.MIN_POOL_SIZE}, max={cls.MAX_POOL_SIZE}")
        logger.info(f"  Timeouts: connection={cls.CONNECTION_TIMEOUT}s, command={cls.COMMAND_TIMEOUT}s")


async def init_db() -> None:
    """
    Initialize the database connection pool.
    
    Raises:
        ConnectionError: If connection to database fails
    """
    global _connection_pool
    
    if _connection_pool is not None:
        logger.warning("Connection pool already initialized")
        return
    
    try:
        logger.info("Initializing database connection pool...")
        DatabaseConfig.log_config()
        
        start_time = time.time()
        
        _connection_pool = await asyncpg.create_pool(
            host=DatabaseConfig.HOST,
            port=DatabaseConfig.PORT,
            database=DatabaseConfig.DATABASE,
            user=DatabaseConfig.USER,
            password=DatabaseConfig.PASSWORD,
            min_size=DatabaseConfig.MIN_POOL_SIZE,
            max_size=DatabaseConfig.MAX_POOL_SIZE,
            timeout=DatabaseConfig.CONNECTION_TIMEOUT,
            command_timeout=DatabaseConfig.COMMAND_TIMEOUT,
            ssl=DatabaseConfig.SSL_MODE if DatabaseConfig.SSL_MODE != 'disable' else None
        )
        
        elapsed_time = time.time() - start_time
        
        # Test the connection
        async with _connection_pool.acquire() as conn:
            version = await conn.fetchval('SELECT version()')
            logger.info(f"✅ Database connected successfully in {elapsed_time:.2f}s")
            logger.info(f"PostgreSQL version: {version[:50]}...")
        
        logger.info(f"Connection pool initialized: {DatabaseConfig.MIN_POOL_SIZE}-{DatabaseConfig.MAX_POOL_SIZE} connections")
        
    except asyncpg.InvalidCatalogNameError as e:
        error_msg = f"Database '{DatabaseConfig.DATABASE}' does not exist"
        logger.error(f"❌ Connection failed: {error_msg}")
        raise ConnectionError(error_msg) from e
    
    except asyncpg.InvalidPasswordError as e:
        error_msg = "Invalid database password"
        logger.error(f"❌ Connection failed: {error_msg}")
        raise ConnectionError(error_msg) from e
    
    except asyncpg.PostgresConnectionError as e:
        error_msg = f"Cannot connect to PostgreSQL server at {DatabaseConfig.HOST}:{DatabaseConfig.PORT}"
        logger.error(f"❌ Connection failed: {error_msg}")
        raise ConnectionError(error_msg) from e
    
    except Exception as e:
        error_msg = f"Unexpected error during database initialization: {str(e)}"
        logger.error(f"❌ {error_msg}")
        raise ConnectionError(error_msg) from e


async def close_db() -> None:
    """
    Close the database connection pool gracefully.
    Waits for all connections to complete their tasks.
    """
    global _connection_pool
    
    if _connection_pool is None:
        logger.warning("Connection pool not initialized, nothing to close")
        return
    
    try:
        logger.info("Closing database connection pool...")
        await _connection_pool.close()
        _connection_pool = None
        logger.info("✅ Connection pool closed successfully")
    
    except Exception as e:
        logger.error(f"❌ Error closing connection pool: {str(e)}")
        raise DatabaseError(f"Failed to close connection pool: {str(e)}") from e


def get_pool() -> asyncpg.Pool:
    """
    Get the current connection pool.
    
    Returns:
        asyncpg.Pool: The connection pool instance
        
    Raises:
        PoolNotInitializedError: If pool hasn't been initialized
    """
    if _connection_pool is None:
        raise PoolNotInitializedError(
            "Database connection pool not initialized. Call init_db() first."
        )
    return _connection_pool


@asynccontextmanager
async def get_connection():
    """
    Get a database connection from the pool (async context manager).
    
    Usage:
        async with get_connection() as conn:
            result = await conn.fetch("SELECT * FROM users")
    
    Yields:
        asyncpg.Connection: A database connection
        
    Raises:
        PoolNotInitializedError: If pool hasn't been initialized
        ConnectionError: If acquiring connection fails
    """
    pool = get_pool()
    
    try:
        async with pool.acquire() as connection:
            yield connection
    except Exception as e:
        logger.error(f"❌ Error acquiring connection: {str(e)}")
        raise ConnectionError(f"Failed to acquire connection: {str(e)}") from e


async def execute(query: str, *args, timeout: Optional[float] = None) -> str:
    """
    Execute a query that doesn't return data (INSERT, UPDATE, DELETE).
    
    Args:
        query: SQL query string
        *args: Query parameters
        timeout: Optional query timeout (overrides default)
    
    Returns:
        str: Query execution status
        
    Raises:
        QueryError: If query execution fails
    """
    start_time = time.time()
    
    try:
        async with get_connection() as conn:
            result = await conn.execute(query, *args, timeout=timeout)
            
        elapsed_time = time.time() - start_time
        logger.debug(f"Query executed in {elapsed_time:.3f}s: {query[:100]}")
        
        return result
    
    except asyncpg.PostgresSyntaxError as e:
        logger.error(f"❌ SQL syntax error: {str(e)}")
        raise QueryError(f"SQL syntax error: {str(e)}") from e
    
    except asyncpg.QueryCanceledError as e:
        logger.error(f"❌ Query canceled (timeout): {str(e)}")
        raise QueryError(f"Query timeout exceeded") from e
    
    except Exception as e:
        logger.error(f"❌ Query execution failed: {str(e)}")
        raise QueryError(f"Query execution failed: {str(e)}") from e


async def fetch_one(query: str, *args, timeout: Optional[float] = None) -> Optional[asyncpg.Record]:
    """
    Fetch a single row from the database.
    
    Args:
        query: SQL query string
        *args: Query parameters
        timeout: Optional query timeout (overrides default)
    
    Returns:
        Optional[asyncpg.Record]: Single row or None if not found
        
    Raises:
        QueryError: If query execution fails
    """
    start_time = time.time()
    
    try:
        async with get_connection() as conn:
            result = await conn.fetchrow(query, *args, timeout=timeout)
        
        elapsed_time = time.time() - start_time
        logger.debug(f"Query executed in {elapsed_time:.3f}s: {query[:100]}")
        
        return result
    
    except asyncpg.PostgresSyntaxError as e:
        logger.error(f"❌ SQL syntax error: {str(e)}")
        raise QueryError(f"SQL syntax error: {str(e)}") from e
    
    except asyncpg.QueryCanceledError as e:
        logger.error(f"❌ Query canceled (timeout): {str(e)}")
        raise QueryError(f"Query timeout exceeded") from e
    
    except Exception as e:
        logger.error(f"❌ Query execution failed: {str(e)}")
        raise QueryError(f"Query execution failed: {str(e)}") from e


async def fetch_all(query: str, *args, timeout: Optional[float] = None) -> List[asyncpg.Record]:
    """
    Fetch all rows from the database.
    
    Args:
        query: SQL query string
        *args: Query parameters
        timeout: Optional query timeout (overrides default)
    
    Returns:
        List[asyncpg.Record]: List of rows (empty list if no results)
        
    Raises:
        QueryError: If query execution fails
    """
    start_time = time.time()
    
    try:
        async with get_connection() as conn:
            results = await conn.fetch(query, *args, timeout=timeout)
        
        elapsed_time = time.time() - start_time
        logger.debug(f"Query returned {len(results)} rows in {elapsed_time:.3f}s: {query[:100]}")
        
        return results
    
    except asyncpg.PostgresSyntaxError as e:
        logger.error(f"❌ SQL syntax error: {str(e)}")
        raise QueryError(f"SQL syntax error: {str(e)}") from e
    
    except asyncpg.QueryCanceledError as e:
        logger.error(f"❌ Query canceled (timeout): {str(e)}")
        raise QueryError(f"Query timeout exceeded") from e
    
    except Exception as e:
        logger.error(f"❌ Query execution failed: {str(e)}")
        raise QueryError(f"Query execution failed: {str(e)}") from e


async def fetch_val(query: str, *args, timeout: Optional[float] = None) -> Any:
    """
    Fetch a single value from the database.
    
    Args:
        query: SQL query string
        *args: Query parameters
        timeout: Optional query timeout (overrides default)
    
    Returns:
        Any: Single value from the first column of the first row
        
    Raises:
        QueryError: If query execution fails
    """
    start_time = time.time()
    
    try:
        async with get_connection() as conn:
            result = await conn.fetchval(query, *args, timeout=timeout)
        
        elapsed_time = time.time() - start_time
        logger.debug(f"Query executed in {elapsed_time:.3f}s: {query[:100]}")
        
        return result
    
    except asyncpg.PostgresSyntaxError as e:
        logger.error(f"❌ SQL syntax error: {str(e)}")
        raise QueryError(f"SQL syntax error: {str(e)}") from e
    
    except asyncpg.QueryCanceledError as e:
        logger.error(f"❌ Query canceled (timeout): {str(e)}")
        raise QueryError(f"Query timeout exceeded") from e
    
    except Exception as e:
        logger.error(f"❌ Query execution failed: {str(e)}")
        raise QueryError(f"Query execution failed: {str(e)}") from e


async def health_check() -> dict:
    """
    Perform a health check on the database connection.
    
    Returns:
        dict: Health check results with status, latency, and details
    """
    start_time = time.time()
    
    try:
        # Test basic connectivity
        result = await fetch_val("SELECT 1")
        
        if result != 1:
            raise QueryError("Health check query returned unexpected result")
        
        # Get database stats
        pool = get_pool()
        pool_size = pool.get_size()
        pool_free = pool.get_idle_size()
        
        # Get PostgreSQL version
        version = await fetch_val("SELECT version()")
        
        latency = time.time() - start_time
        
        health_status = {
            "status": "healthy",
            "latency_ms": round(latency * 1000, 2),
            "pool_size": pool_size,
            "pool_free": pool_free,
            "pool_active": pool_size - pool_free,
            "database": DatabaseConfig.DATABASE,
            "host": DatabaseConfig.HOST,
            "port": DatabaseConfig.PORT,
            "postgresql_version": version.split(',')[0] if version else "Unknown"
        }
        
        logger.info(f"✅ Health check passed: latency={health_status['latency_ms']}ms")
        return health_status
    
    except Exception as e:
        logger.error(f"❌ Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "database": DatabaseConfig.DATABASE,
            "host": DatabaseConfig.HOST,
            "port": DatabaseConfig.PORT
        }


async def test_connection():
    """
    Test database connection with example queries.
    
    Usage example demonstrating the connection module.
    """
    print("=" * 60)
    print("REIMS Database Connection Test")
    print("=" * 60)
    
    try:
        # Initialize connection pool
        print("\n1. Initializing connection pool...")
        await init_db()
        print("✅ Connection pool initialized")
        
        # Test fetch_val
        print("\n2. Testing fetch_val (single value)...")
        result = await fetch_val("SELECT 1 as test_value")
        print(f"✅ Result: {result}")
        
        # Test fetch_one
        print("\n3. Testing fetch_one (single row)...")
        result = await fetch_one("SELECT 1 as id, 'test' as name, NOW() as timestamp")
        if result:
            print(f"✅ Result: id={result['id']}, name={result['name']}, timestamp={result['timestamp']}")
        
        # Test fetch_all
        print("\n4. Testing fetch_all (multiple rows)...")
        result = await fetch_all("""
            SELECT 
                generate_series(1, 5) as id,
                'Property ' || generate_series(1, 5) as name
        """)
        print(f"✅ Retrieved {len(result)} rows:")
        for row in result:
            print(f"   - {row['id']}: {row['name']}")
        
        # Test health check
        print("\n5. Testing health check...")
        health = await health_check()
        print(f"✅ Health check: {health}")
        
        # Test execute (create temporary table)
        print("\n6. Testing execute (INSERT/UPDATE/DELETE)...")
        await execute("""
            CREATE TEMPORARY TABLE test_table (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        await execute("INSERT INTO test_table (name) VALUES ($1)", "Test Property")
        count = await fetch_val("SELECT COUNT(*) FROM test_table")
        print(f"✅ Inserted 1 row, total count: {count}")
        
        print("\n" + "=" * 60)
        print("✅ All tests passed successfully!")
        print("=" * 60)
        
    except ConnectionError as e:
        print(f"\n❌ Connection failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Check if PostgreSQL is running")
        print("  2. Verify DATABASE_* environment variables")
        print("  3. Check firewall/network settings")
        print("  4. Verify database exists and user has access")
    
    except QueryError as e:
        print(f"\n❌ Query execution failed: {e}")
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    
    finally:
        # Clean up
        print("\n7. Closing connection pool...")
        await close_db()
        print("✅ Connection pool closed")


# Main entry point for testing
if __name__ == "__main__":
    import asyncio
    
    # Run the test
    asyncio.run(test_connection())

















"""
REIMS FastAPI Dependencies
Provides dependency injection for Redis, MinIO, and other services
"""

import redis
from minio import Minio
import os
from typing import Optional

# --- Redis Configuration ---
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# --- MinIO Configuration ---
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_SECURE = os.getenv("MINIO_SECURE", "False").lower() == "true"


def get_redis_client() -> Optional[redis.Redis]:
    """
    FastAPI dependency for Redis client.
    
    Yields:
        redis.Redis: Redis client instance or None if unavailable
        
    Usage:
        @app.get("/items")
        def get_items(redis_client: redis.Redis = Depends(get_redis_client)):
            cached = redis_client.get("items")
    """
    client = None
    try:
        client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2
        )
        # Test connection
        client.ping()
    except redis.exceptions.ConnectionError as e:
        print(f"WARNING: Redis connection error: {e}")
        client = None
    except Exception as e:
        print(f"WARNING: Unexpected Redis error: {e}")
        client = None
    
    yield client
    
    # Cleanup (no-op, connection pool handles this)


def get_minio_client() -> Optional[Minio]:
    """
    FastAPI dependency for MinIO client.
    
    Yields:
        Minio: MinIO client instance or None if unavailable
        
    Usage:
        @app.post("/upload")
        def upload(minio_client: Minio = Depends(get_minio_client)):
            minio_client.put_object(...)
    """
    client = None
    try:
        client = Minio(
            endpoint=MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=MINIO_SECURE
        )
    except Exception as e:
        print(f"WARNING: MinIO connection error: {e}")
        client = None
    
    yield client
    
    # Cleanup (no-op, client is stateless)


# Singleton instances (optional, for non-request-scoped usage)
_redis_client: Optional[redis.Redis] = None
_minio_client: Optional[Minio] = None


def get_redis_singleton() -> Optional[redis.Redis]:
    """
    Get a singleton Redis client (not request-scoped).
    Use this for background tasks or startup events.
    """
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                decode_responses=True
            )
            _redis_client.ping()
            print("SUCCESS: Redis connected")
        except Exception as e:
            print(f"WARNING: Redis not available: {e}")
            _redis_client = None
    return _redis_client


def get_minio_singleton() -> Optional[Minio]:
    """
    Get a singleton MinIO client (not request-scoped).
    Use this for background tasks or startup events.
    """
    global _minio_client
    if _minio_client is None:
        try:
            _minio_client = Minio(
                endpoint=MINIO_ENDPOINT,
                access_key=MINIO_ACCESS_KEY,
                secret_key=MINIO_SECRET_KEY,
                secure=MINIO_SECURE
            )
            print("SUCCESS: MinIO connected")
        except Exception as e:
            print(f"WARNING: MinIO not available: {e}")
            _minio_client = None
    return _minio_client


def close_connections():
    """
    Close all singleton connections.
    Call this during application shutdown.
    """
    global _redis_client, _minio_client
    
    if _redis_client:
        try:
            _redis_client.close()
            print("SUCCESS: Redis connection closed")
        except:
            pass
        _redis_client = None
    
    _minio_client = None
    print("SUCCESS: All connections closed")

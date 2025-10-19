"""
REIMS Health Check Endpoint

Comprehensive health check for all infrastructure services:
- PostgreSQL Database
- Redis Cache
- MinIO Storage
- Ollama AI

Author: REIMS Development Team
Date: October 12, 2025
"""

import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Tuple
from fastapi import APIRouter, Response, status
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(tags=["health"])


# ============================================================================
# Service Health Check Functions
# ============================================================================

async def check_database_health() -> Tuple[str, Dict[str, Any]]:
    """
    Check PostgreSQL database health.
    
    Returns:
        Tuple of (status, details)
    """
    try:
        from backend.db import health_check
        
        start_time = time.time()
        health_data = await health_check()
        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        
        if health_data.get("status") == "healthy":
            return "healthy", {
                "latency_ms": health_data.get("latency_ms", elapsed_ms),
                "pool_size": health_data.get("pool_size", 0),
                "pool_free": health_data.get("pool_free", 0),
                "pool_active": health_data.get("pool_active", 0),
                "database": health_data.get("database", "reims"),
                "version": health_data.get("postgresql_version", "Unknown")[:30]
            }
        else:
            return "unhealthy", {
                "error": health_data.get("error", "Unknown error"),
                "latency_ms": elapsed_ms
            }
    
    except ImportError:
        # Database module not initialized yet
        logger.warning("Database module not available, attempting direct check...")
        return await check_database_fallback()
    
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return "unhealthy", {
            "error": str(e),
            "message": "Database connection failed"
        }


async def check_database_fallback() -> Tuple[str, Dict[str, Any]]:
    """
    Fallback database check without connection pool.
    """
    try:
        import asyncpg
        
        start_time = time.time()
        
        conn = await asyncpg.connect(
            host=os.getenv('DATABASE_HOST', 'localhost'),
            port=int(os.getenv('DATABASE_PORT', '5432')),
            database=os.getenv('DATABASE_NAME', 'reims'),
            user=os.getenv('DATABASE_USER', 'postgres'),
            password=os.getenv('DATABASE_PASSWORD', ''),
            timeout=5.0
        )
        
        result = await conn.fetchval('SELECT 1')
        await conn.close()
        
        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        
        if result == 1:
            return "healthy", {
                "latency_ms": elapsed_ms,
                "connection_type": "direct",
                "message": "Direct connection successful"
            }
        else:
            return "unhealthy", {
                "error": "Query returned unexpected result"
            }
    
    except Exception as e:
        return "unhealthy", {
            "error": str(e),
            "message": "Direct connection failed"
        }


async def check_redis_health() -> Tuple[str, Dict[str, Any]]:
    """
    Check Redis cache health.
    
    Returns:
        Tuple of (status, details)
    """
    try:
        import redis.asyncio as redis
        
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', '6379'))
        redis_password = os.getenv('REDIS_PASSWORD', None)
        
        start_time = time.time()
        
        # Create Redis client
        client = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        
        # Test PING
        ping_result = await client.ping()
        
        # Get server info
        info = await client.info('memory')
        
        # Get stats
        stats = await client.info('stats')
        
        await client.aclose()
        
        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        
        if ping_result:
            return "healthy", {
                "latency_ms": elapsed_ms,
                "memory_usage": info.get('used_memory_human', 'Unknown'),
                "memory_peak": info.get('used_memory_peak_human', 'Unknown'),
                "connected_clients": stats.get('connected_clients', 0),
                "total_commands": stats.get('total_commands_processed', 0),
                "version": info.get('redis_version', 'Unknown')
            }
        else:
            return "unhealthy", {
                "error": "PING failed",
                "latency_ms": elapsed_ms
            }
    
    except ImportError:
        logger.warning("redis package not installed")
        return "unavailable", {
            "message": "Redis client not available (redis package not installed)"
        }
    
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")
        return "unhealthy", {
            "error": str(e),
            "message": "Redis connection failed"
        }


async def check_minio_health() -> Tuple[str, Dict[str, Any]]:
    """
    Check MinIO storage health.
    
    Returns:
        Tuple of (status, details)
    """
    try:
        from minio import Minio
        from minio.error import S3Error
        
        minio_endpoint = os.getenv('MINIO_ENDPOINT', 'localhost:9000')
        minio_access_key = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
        minio_secret_key = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
        minio_secure = os.getenv('MINIO_SECURE', 'False').lower() == 'true'
        
        start_time = time.time()
        
        # Create MinIO client
        client = Minio(
            minio_endpoint,
            access_key=minio_access_key,
            secret_key=minio_secret_key,
            secure=minio_secure
        )
        
        # List buckets (lightweight operation)
        buckets = list(client.list_buckets())
        
        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        
        return "healthy", {
            "latency_ms": elapsed_ms,
            "buckets_count": len(buckets),
            "buckets": [b.name for b in buckets[:5]],  # First 5 buckets
            "endpoint": minio_endpoint,
            "secure": minio_secure
        }
    
    except ImportError:
        logger.warning("minio package not installed")
        return "unavailable", {
            "message": "MinIO client not available (minio package not installed)"
        }
    
    except S3Error as e:
        logger.error(f"MinIO S3 error: {str(e)}")
        return "unhealthy", {
            "error": str(e),
            "message": "MinIO S3 error"
        }
    
    except Exception as e:
        logger.error(f"MinIO health check failed: {str(e)}")
        return "unhealthy", {
            "error": str(e),
            "message": "MinIO connection failed"
        }


async def check_ollama_health() -> Tuple[str, Dict[str, Any]]:
    """
    Check Ollama AI service health.
    
    Returns:
        Tuple of (status, details)
    """
    try:
        import httpx
        
        ollama_host = os.getenv('OLLAMA_HOST', 'localhost')
        ollama_port = os.getenv('OLLAMA_PORT', '11434')
        ollama_url = f"http://{ollama_host}:{ollama_port}"
        
        start_time = time.time()
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Check if Ollama is running
            response = await client.get(f"{ollama_url}/api/tags")
            
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            
            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])
                
                return "healthy", {
                    "latency_ms": elapsed_ms,
                    "models_count": len(models),
                    "models": [m.get('name', 'Unknown') for m in models[:3]],  # First 3 models
                    "endpoint": ollama_url,
                    "status_code": response.status_code
                }
            else:
                return "unhealthy", {
                    "error": f"HTTP {response.status_code}",
                    "latency_ms": elapsed_ms,
                    "message": "Ollama returned non-200 status"
                }
    
    except ImportError:
        logger.warning("httpx package not installed")
        return "unavailable", {
            "message": "Ollama client not available (httpx package not installed)"
        }
    
    except httpx.ConnectError as e:
        logger.warning(f"Ollama not reachable: {str(e)}")
        return "unhealthy", {
            "error": "Connection refused",
            "message": "Ollama service not reachable"
        }
    
    except httpx.TimeoutException:
        logger.error("Ollama health check timed out")
        return "unhealthy", {
            "error": "Timeout",
            "message": "Ollama request timed out"
        }
    
    except Exception as e:
        logger.error(f"Ollama health check failed: {str(e)}")
        return "unhealthy", {
            "error": str(e),
            "message": "Ollama health check failed"
        }


# ============================================================================
# Health Check Endpoint
# ============================================================================

@router.get("/health")
async def health_check_endpoint(response: Response) -> Dict[str, Any]:
    """
    Comprehensive health check for all REIMS services.
    
    Returns:
        - 200 OK: All services healthy or degraded
        - 503 Service Unavailable: Critical services unhealthy
    
    Response includes:
        - Overall status (healthy, degraded, unhealthy)
        - Individual service statuses
        - Detailed metrics for each service
        - Timestamp
    """
    start_time = time.time()
    
    # Check all services
    logger.info("Running health checks for all services...")
    
    db_status, db_details = await check_database_health()
    redis_status, redis_details = await check_redis_health()
    minio_status, minio_details = await check_minio_health()
    ollama_status, ollama_details = await check_ollama_health()
    
    # Compile service statuses
    services = {
        "database": db_status,
        "redis": redis_status,
        "minio": minio_status,
        "ollama": ollama_status
    }
    
    # Compile detailed information
    details = {
        "database": db_details,
        "redis": redis_details,
        "minio": minio_details,
        "ollama": ollama_details
    }
    
    # Determine overall status
    unhealthy_count = sum(1 for s in services.values() if s == "unhealthy")
    unavailable_count = sum(1 for s in services.values() if s == "unavailable")
    
    # Overall status logic:
    # - healthy: All services healthy or unavailable (optional services)
    # - degraded: Database healthy, but other services have issues
    # - unhealthy: Database unhealthy (critical)
    
    if db_status == "unhealthy":
        overall_status = "unhealthy"
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE
        success = False
    elif unhealthy_count > 0:
        overall_status = "degraded"
        http_status = status.HTTP_200_OK
        success = True
    else:
        overall_status = "healthy"
        http_status = status.HTTP_200_OK
        success = True
    
    # Calculate total check time
    total_time_ms = round((time.time() - start_time) * 1000, 2)
    
    # Build response
    health_response = {
        "success": success,
        "status": overall_status,
        "services": services,
        "details": details,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "check_duration_ms": total_time_ms
    }
    
    # Set HTTP status code
    response.status_code = http_status
    
    # Log results
    if overall_status == "healthy":
        logger.info(f"✅ Health check passed: All services healthy ({total_time_ms}ms)")
    elif overall_status == "degraded":
        logger.warning(f"⚠️ Health check degraded: {unhealthy_count} service(s) unhealthy ({total_time_ms}ms)")
    else:
        logger.error(f"❌ Health check failed: Database unhealthy ({total_time_ms}ms)")
    
    return health_response


@router.get("/health/database")
async def database_health_endpoint() -> Dict[str, Any]:
    """
    Database-only health check endpoint.
    
    Returns detailed PostgreSQL health information.
    """
    db_status, db_details = await check_database_health()
    
    return {
        "success": db_status == "healthy",
        "status": db_status,
        "details": db_details,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/health/redis")
async def redis_health_endpoint() -> Dict[str, Any]:
    """
    Redis-only health check endpoint.
    
    Returns detailed Redis health information.
    """
    redis_status, redis_details = await check_redis_health()
    
    return {
        "success": redis_status == "healthy",
        "status": redis_status,
        "details": redis_details,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/health/minio")
async def minio_health_endpoint() -> Dict[str, Any]:
    """
    MinIO-only health check endpoint.
    
    Returns detailed MinIO health information.
    """
    minio_status, minio_details = await check_minio_health()
    
    return {
        "success": minio_status == "healthy",
        "status": minio_status,
        "details": minio_details,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/health/ollama")
async def ollama_health_endpoint() -> Dict[str, Any]:
    """
    Ollama-only health check endpoint.
    
    Returns detailed Ollama health information.
    """
    ollama_status, ollama_details = await check_ollama_health()
    
    return {
        "success": ollama_status == "healthy",
        "status": ollama_status,
        "details": ollama_details,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/health/live")
async def liveness_probe() -> Dict[str, str]:
    """
    Kubernetes liveness probe endpoint.
    
    Returns 200 OK if the application is running.
    This is a lightweight check that doesn't test external dependencies.
    """
    return {
        "status": "alive",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/health/ready")
async def readiness_probe(response: Response) -> Dict[str, Any]:
    """
    Kubernetes readiness probe endpoint.
    
    Returns 200 OK only if critical services (database) are healthy.
    Returns 503 if not ready to serve traffic.
    """
    db_status, db_details = await check_database_health()
    
    if db_status == "healthy":
        return {
            "status": "ready",
            "database": db_status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    else:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "not_ready",
            "database": db_status,
            "details": db_details,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# ============================================================================
# Startup check (optional)
# ============================================================================

async def startup_health_check():
    """
    Run health checks on application startup.
    Call this from your FastAPI lifespan manager.
    """
    logger.info("=" * 60)
    logger.info("Running startup health checks...")
    logger.info("=" * 60)
    
    db_status, db_details = await check_database_health()
    logger.info(f"Database: {db_status} - {db_details}")
    
    redis_status, redis_details = await check_redis_health()
    logger.info(f"Redis: {redis_status} - {redis_details}")
    
    minio_status, minio_details = await check_minio_health()
    logger.info(f"MinIO: {minio_status} - {minio_details}")
    
    ollama_status, ollama_details = await check_ollama_health()
    logger.info(f"Ollama: {ollama_status} - {ollama_details}")
    
    logger.info("=" * 60)
    
    # Return summary
    return {
        "database": db_status,
        "redis": redis_status,
        "minio": minio_status,
        "ollama": ollama_status
    }

















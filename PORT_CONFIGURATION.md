# REIMS System Port Configuration
# This file documents the standard ports used by all REIMS services

## Frontend Services
FRONTEND_PORT=5173
FRONTEND_URL=http://localhost:5173

## Backend Services  
BACKEND_PORT=8001
BACKEND_URL=http://localhost:8001

## Storage Services
MINIO_API_PORT=9000
MINIO_CONSOLE_PORT=9001
STORAGE_SERVICE_PORT=8002

## Database Services
REDIS_PORT=6379
POSTGRESQL_PORT=5432 (fallback to SQLite)

## Service Dependencies
# Frontend -> Backend: http://localhost:8001
# Backend -> MinIO: http://localhost:9000
# Backend -> Redis: localhost:6379
# Backend -> Storage Service: http://localhost:8002

## Notes
- All services should use these fixed ports
- No automatic port switching allowed
- If port is in use, service should fail with clear error message
- CORS is configured specifically for port 5173 only
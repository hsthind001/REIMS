# REIMS Health Check Endpoint - Complete Guide

**Created:** October 12, 2025  
**Status:** ✅ Production Ready  
**Location:** `backend/api/health.py`

---

## 📋 Overview

Comprehensive health check endpoint that monitors all REIMS infrastructure services:

- ✅ **PostgreSQL Database** - Connection pool stats & latency
- ✅ **Redis Cache** - Memory usage & connectivity
- ✅ **MinIO Storage** - Bucket access & latency
- ✅ **Ollama AI** - Model availability & response time

---

## 🚀 Endpoints

### 1. Main Health Check: `GET /health`

**Description:** Checks all services and returns comprehensive health status.

**Response Codes:**
- `200 OK` - All services healthy or degraded (non-critical issues)
- `503 Service Unavailable` - Critical services (database) unhealthy

**Response Format:**
```json
{
  "success": true,
  "status": "healthy",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "minio": "healthy",
    "ollama": "healthy"
  },
  "details": {
    "database": {
      "latency_ms": 12.45,
      "pool_size": 15,
      "pool_free": 10,
      "pool_active": 5,
      "database": "reims",
      "version": "PostgreSQL 15.2"
    },
    "redis": {
      "latency_ms": 3.21,
      "memory_usage": "1.2MB",
      "memory_peak": "2.5MB",
      "connected_clients": 3,
      "total_commands": 15420,
      "version": "7.0.5"
    },
    "minio": {
      "latency_ms": 45.67,
      "buckets_count": 4,
      "buckets": ["reims-uploads", "reims-documents", "reims-backups"],
      "endpoint": "localhost:9000",
      "secure": false
    },
    "ollama": {
      "latency_ms": 150.34,
      "models_count": 2,
      "models": ["llama2", "mistral"],
      "endpoint": "http://localhost:11434",
      "status_code": 200
    }
  },
  "timestamp": "2025-10-12T19:32:53.123Z",
  "check_duration_ms": 234.56
}
```

**Status Values:**
- `healthy` - Service operational
- `degraded` - Some services have issues (non-critical)
- `unhealthy` - Critical services down
- `unavailable` - Service not configured/optional

---

### 2. Database Health: `GET /health/database`

**Description:** Database-only health check.

**Response:**
```json
{
  "success": true,
  "status": "healthy",
  "details": {
    "latency_ms": 12.45,
    "pool_size": 15,
    "pool_free": 10,
    "pool_active": 5,
    "database": "reims",
    "version": "PostgreSQL 15.2"
  },
  "timestamp": "2025-10-12T19:32:53Z"
}
```

---

### 3. Redis Health: `GET /health/redis`

**Description:** Redis-only health check.

**Response:**
```json
{
  "success": true,
  "status": "healthy",
  "details": {
    "latency_ms": 3.21,
    "memory_usage": "1.2MB",
    "memory_peak": "2.5MB",
    "connected_clients": 3,
    "total_commands": 15420,
    "version": "7.0.5"
  },
  "timestamp": "2025-10-12T19:32:53Z"
}
```

---

### 4. MinIO Health: `GET /health/minio`

**Description:** MinIO-only health check.

**Response:**
```json
{
  "success": true,
  "status": "healthy",
  "details": {
    "latency_ms": 45.67,
    "buckets_count": 4,
    "buckets": ["reims-uploads", "reims-documents"],
    "endpoint": "localhost:9000",
    "secure": false
  },
  "timestamp": "2025-10-12T19:32:53Z"
}
```

---

### 5. Ollama Health: `GET /health/ollama`

**Description:** Ollama AI service health check.

**Response:**
```json
{
  "success": true,
  "status": "healthy",
  "details": {
    "latency_ms": 150.34,
    "models_count": 2,
    "models": ["llama2", "mistral"],
    "endpoint": "http://localhost:11434",
    "status_code": 200
  },
  "timestamp": "2025-10-12T19:32:53Z"
}
```

---

### 6. Liveness Probe: `GET /health/live`

**Description:** Lightweight check for Kubernetes liveness probe. Always returns 200 if app is running.

**Response:**
```json
{
  "status": "alive",
  "timestamp": "2025-10-12T19:32:53Z"
}
```

---

### 7. Readiness Probe: `GET /health/ready`

**Description:** Kubernetes readiness probe. Returns 200 only if database is healthy.

**Response Codes:**
- `200 OK` - Ready to serve traffic
- `503 Service Unavailable` - Not ready

**Response:**
```json
{
  "status": "ready",
  "database": "healthy",
  "timestamp": "2025-10-12T19:32:53Z"
}
```

---

## 🔧 Integration with FastAPI

### Step 1: Import and Register Router

In your main backend file (e.g., `start_optimized_server.py`):

```python
from fastapi import FastAPI
from backend.api.health import router as health_router

app = FastAPI(title="REIMS API", version="2.0")

# Register health check router
app.include_router(health_router)
```

### Step 2: Add Startup Health Check (Optional)

```python
from contextlib import asynccontextmanager
from backend.api.health import startup_health_check
from backend.db import init_db, close_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting REIMS application...")
    
    # Initialize database
    await init_db()
    
    # Run health checks
    health_status = await startup_health_check()
    
    yield  # Application runs
    
    # Shutdown
    print("🛑 Shutting down REIMS...")
    await close_db()

app = FastAPI(lifespan=lifespan)
```

---

## 🌐 Environment Variables

Configure service connections in `.env`:

```env
# Database (required)
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=reims
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password

# Redis (optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# MinIO (optional)
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=false

# Ollama (optional)
OLLAMA_HOST=localhost
OLLAMA_PORT=11434
```

---

## 💻 Usage Examples

### Example 1: cURL

```bash
# Check all services
curl http://localhost:8000/health

# Check specific service
curl http://localhost:8000/health/database
curl http://localhost:8000/health/redis
curl http://localhost:8000/health/minio
curl http://localhost:8000/health/ollama

# Kubernetes probes
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready
```

### Example 2: Python Client

```python
import httpx
import asyncio

async def check_health():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/health")
        health = response.json()
        
        print(f"Status: {health['status']}")
        print(f"Services: {health['services']}")
        
        if health['status'] != 'healthy':
            print(f"⚠️ Health check degraded or unhealthy!")
            
        return health

# Run
asyncio.run(check_health())
```

### Example 3: Frontend Integration (JavaScript)

```javascript
// Check health every 30 seconds
async function checkHealth() {
  try {
    const response = await fetch('http://localhost:8000/health');
    const health = await response.json();
    
    console.log('Health Status:', health.status);
    
    // Update UI based on status
    if (health.status === 'healthy') {
      updateHealthIndicator('green', 'All systems operational');
    } else if (health.status === 'degraded') {
      updateHealthIndicator('yellow', 'Some services degraded');
    } else {
      updateHealthIndicator('red', 'System unhealthy');
    }
    
    // Show detailed info
    console.table(health.services);
    console.table(health.details);
    
  } catch (error) {
    console.error('Health check failed:', error);
    updateHealthIndicator('red', 'Cannot reach backend');
  }
}

// Check every 30 seconds
setInterval(checkHealth, 30000);

// Initial check
checkHealth();
```

### Example 4: React Component

```jsx
import { useState, useEffect } from 'react';

function HealthIndicator() {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch('http://localhost:8000/health');
        const data = await response.json();
        setHealth(data);
      } catch (error) {
        console.error('Health check failed:', error);
      } finally {
        setLoading(false);
      }
    };
    
    checkHealth();
    const interval = setInterval(checkHealth, 30000); // 30 seconds
    
    return () => clearInterval(interval);
  }, []);
  
  if (loading) return <div>Checking system health...</div>;
  
  const getStatusColor = (status) => {
    if (status === 'healthy') return '#22c55e'; // green
    if (status === 'degraded') return '#f59e0b'; // yellow
    return '#ef4444'; // red
  };
  
  return (
    <div className="health-indicator">
      <div 
        className="status-dot" 
        style={{ backgroundColor: getStatusColor(health?.status) }}
      />
      <span>{health?.status || 'Unknown'}</span>
      
      {/* Service details */}
      <div className="services">
        {Object.entries(health?.services || {}).map(([name, status]) => (
          <div key={name} className="service-item">
            <span>{name}</span>
            <span className={`status-${status}`}>{status}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default HealthIndicator;
```

---

## 🐳 Kubernetes Configuration

### Deployment with Health Checks

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: reims-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: reims-backend
  template:
    metadata:
      labels:
        app: reims-backend
    spec:
      containers:
      - name: reims-backend
        image: reims-backend:latest
        ports:
        - containerPort: 8000
        
        # Liveness probe - restart if failing
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        
        # Readiness probe - remove from service if failing
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          successThreshold: 1
          failureThreshold: 2
        
        # Startup probe - give more time on startup
        startupProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 0
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 30  # 30 * 5 = 150 seconds max
```

---

## 📊 Monitoring & Alerting

### Example 1: Prometheus Monitoring

```python
# Add Prometheus metrics to health endpoint
from prometheus_client import Gauge

health_status = Gauge('reims_service_health', 'Service health status', ['service'])

@router.get("/health")
async def health_check_endpoint(response: Response):
    # ... existing code ...
    
    # Update Prometheus metrics
    for service, status in services.items():
        health_status.labels(service=service).set(
            1 if status == 'healthy' else 0
        )
    
    return health_response
```

### Example 2: Alert on Degraded Status

```python
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

async def send_alert(service: str, status: str, details: dict):
    """Send alert when service becomes unhealthy"""
    message = f"""
    🚨 REIMS Health Alert
    
    Service: {service}
    Status: {status}
    Time: {datetime.now().isoformat()}
    Details: {details}
    """
    
    logger.critical(message)
    
    # Send to alerting system (PagerDuty, Slack, email, etc.)
    # await send_pagerduty_alert(message)
    # await send_slack_alert(message)
```

---

## 🧪 Testing

### Test the Endpoint

```bash
# Start backend
python start_optimized_server.py

# Test main health check
curl http://localhost:8000/health | jq

# Test individual services
curl http://localhost:8000/health/database | jq
curl http://localhost:8000/health/redis | jq
curl http://localhost:8000/health/minio | jq
curl http://localhost:8000/health/ollama | jq

# Test Kubernetes probes
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready
```

### Expected Output (All Healthy)

```json
{
  "success": true,
  "status": "healthy",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "minio": "healthy",
    "ollama": "healthy"
  },
  "details": { ... },
  "timestamp": "2025-10-12T19:32:53.123456Z",
  "check_duration_ms": 234.56
}
```

---

## 🐛 Troubleshooting

### Issue: Database shows "unhealthy"

**Symptoms:**
```json
{
  "database": "unhealthy",
  "details": {
    "database": {
      "error": "Cannot connect to PostgreSQL server"
    }
  }
}
```

**Solutions:**
1. Check PostgreSQL is running
2. Verify `.env` database credentials
3. Test connection: `psql -h localhost -U postgres -d reims`
4. Check database logs

---

### Issue: Redis shows "unavailable"

**Symptoms:**
```json
{
  "redis": "unavailable",
  "details": {
    "redis": {
      "message": "Redis client not available"
    }
  }
}
```

**Solutions:**
1. Install Redis client: `pip install redis[hiredis]`
2. Start Redis: `redis-server` or `docker run -d -p 6379:6379 redis`
3. Verify connection: `redis-cli ping`

---

### Issue: MinIO shows "unhealthy"

**Symptoms:**
```json
{
  "minio": "unhealthy",
  "details": {
    "minio": {
      "error": "Connection refused"
    }
  }
}
```

**Solutions:**
1. Install MinIO client: `pip install minio`
2. Start MinIO: `minio.exe server ./minio-data`
3. Verify endpoint in `.env`: `MINIO_ENDPOINT=localhost:9000`
4. Check MinIO console: `http://localhost:9001`

---

### Issue: Ollama shows "unhealthy"

**Symptoms:**
```json
{
  "ollama": "unhealthy",
  "details": {
    "ollama": {
      "error": "Connection refused"
    }
  }
}
```

**Solutions:**
1. Install httpx: `pip install httpx`
2. Start Ollama: `ollama serve`
3. Verify Ollama is running: `ollama list`
4. Check endpoint: `curl http://localhost:11434/api/tags`

---

## 📦 Files Created

1. **`backend/api/health.py`** (600+ lines)
   - Main health check endpoint
   - Individual service checks
   - Kubernetes probes
   - Startup health check

2. **`backend/api/__init__.py`**
   - Package exports

3. **`HEALTH_CHECK_ENDPOINT.md`** (this file)
   - Complete documentation
   - Usage examples
   - Integration guides

---

## ✅ Features Delivered

- [x] Main `/health` endpoint with all services
- [x] Individual service endpoints (`/health/database`, etc.)
- [x] PostgreSQL health check with pool stats
- [x] Redis health check with memory stats
- [x] MinIO health check with bucket listing
- [x] Ollama health check with model info
- [x] Latency measurement for all services
- [x] Appropriate HTTP status codes (200, 503)
- [x] Kubernetes liveness probe (`/health/live`)
- [x] Kubernetes readiness probe (`/health/ready`)
- [x] Detailed error messages
- [x] Startup health check function
- [x] Comprehensive logging
- [x] Zero linting errors

---

## 🎯 Next Steps

1. **Register the router** in your main FastAPI app
2. **Install optional dependencies** (redis, minio, httpx)
3. **Configure environment variables**
4. **Test all endpoints**
5. **Integrate with frontend** (30-second polling)
6. **Set up monitoring** (Prometheus, alerts)
7. **Configure Kubernetes probes** (if using K8s)

---

## 📚 Related Documentation

- `DATABASE_CONNECTION_MODULE.md` - Database connection module
- `backend/db/README.md` - Database API reference
- `HOW_TO_USE_DATABASE_MODULE.md` - Database integration guide

---

**REIMS Development Team**  
October 12, 2025  
🚀 Production Ready

















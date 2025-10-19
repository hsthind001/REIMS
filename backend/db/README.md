# REIMS Database Connection Module

Async PostgreSQL connection management using `asyncpg`.

## Features

- ✅ Async connection pool (10-20 connections)
- ✅ Environment-based configuration
- ✅ Comprehensive error handling
- ✅ Query execution logging with timings
- ✅ Health check functionality
- ✅ SSL support for production
- ✅ Graceful connection cleanup

## Installation

```bash
pip install asyncpg python-dotenv
```

## Environment Variables

Create a `.env` file in your project root:

```env
# Database Configuration
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=reims
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password_here

# Optional
ENVIRONMENT=development  # or 'production' for SSL
```

## Quick Start

### 1. Initialize Connection Pool

```python
from backend.db import init_db, close_db

# Initialize pool (call once at startup)
await init_db()

# Close pool (call on shutdown)
await close_db()
```

### 2. Execute Queries

```python
from backend.db import fetch_all, fetch_one, fetch_val, execute

# Fetch all rows
properties = await fetch_all("SELECT * FROM properties WHERE city = $1", "Los Angeles")

# Fetch single row
property = await fetch_one("SELECT * FROM properties WHERE id = $1", 123)

# Fetch single value
count = await fetch_val("SELECT COUNT(*) FROM properties")

# Execute INSERT/UPDATE/DELETE
await execute(
    "INSERT INTO properties (name, address) VALUES ($1, $2)",
    "New Property", "123 Main St"
)
```

### 3. Use Connection Context Manager

```python
from backend.db import get_connection

async with get_connection() as conn:
    # Use connection for multiple queries
    await conn.execute("BEGIN")
    await conn.execute("INSERT INTO ...")
    await conn.execute("UPDATE ...")
    await conn.execute("COMMIT")
```

### 4. Health Check

```python
from backend.db import health_check

# Check database health
status = await health_check()
print(status)
# {
#     "status": "healthy",
#     "latency_ms": 12.34,
#     "pool_size": 15,
#     "pool_free": 10,
#     "pool_active": 5,
#     ...
# }
```

## API Reference

### Core Functions

#### `init_db() -> None`
Initialize the connection pool. Call once at application startup.

**Raises:**
- `ConnectionError`: If connection fails

**Example:**
```python
await init_db()
```

---

#### `close_db() -> None`
Close the connection pool gracefully. Call on application shutdown.

**Example:**
```python
await close_db()
```

---

#### `get_connection() -> AsyncContextManager[asyncpg.Connection]`
Get a database connection from the pool.

**Returns:** Async context manager yielding a connection

**Example:**
```python
async with get_connection() as conn:
    result = await conn.fetch("SELECT * FROM users")
```

---

#### `health_check() -> dict`
Perform database health check.

**Returns:** Dict with health status and metrics

**Example:**
```python
health = await health_check()
if health['status'] == 'healthy':
    print(f"DB is healthy, latency: {health['latency_ms']}ms")
```

---

### Query Functions

#### `execute(query: str, *args, timeout: Optional[float] = None) -> str`
Execute a query that doesn't return data (INSERT, UPDATE, DELETE).

**Parameters:**
- `query`: SQL query string
- `*args`: Query parameters (use $1, $2, etc.)
- `timeout`: Optional timeout in seconds

**Returns:** Query execution status

**Example:**
```python
await execute(
    "UPDATE properties SET status = $1 WHERE id = $2",
    "active", 123
)
```

---

#### `fetch_one(query: str, *args, timeout: Optional[float] = None) -> Optional[Record]`
Fetch a single row.

**Parameters:**
- `query`: SQL query string
- `*args`: Query parameters
- `timeout`: Optional timeout in seconds

**Returns:** Single row or None

**Example:**
```python
user = await fetch_one("SELECT * FROM users WHERE email = $1", "user@example.com")
if user:
    print(f"User: {user['name']}")
```

---

#### `fetch_all(query: str, *args, timeout: Optional[float] = None) -> List[Record]`
Fetch all rows.

**Parameters:**
- `query`: SQL query string
- `*args`: Query parameters
- `timeout`: Optional timeout in seconds

**Returns:** List of rows (empty list if no results)

**Example:**
```python
properties = await fetch_all(
    "SELECT * FROM properties WHERE city = $1 AND price < $2",
    "New York", 1000000
)
```

---

#### `fetch_val(query: str, *args, timeout: Optional[float] = None) -> Any`
Fetch a single value.

**Parameters:**
- `query`: SQL query string
- `*args`: Query parameters
- `timeout`: Optional timeout in seconds

**Returns:** Single value

**Example:**
```python
total_revenue = await fetch_val(
    "SELECT SUM(rent) FROM leases WHERE status = $1",
    "active"
)
```

---

## Exception Handling

The module provides custom exceptions for better error handling:

```python
from backend.db import DatabaseError, ConnectionError, QueryError, PoolNotInitializedError

try:
    await init_db()
    result = await fetch_all("SELECT * FROM properties")
except ConnectionError as e:
    print(f"Failed to connect: {e}")
except QueryError as e:
    print(f"Query failed: {e}")
except PoolNotInitializedError as e:
    print(f"Pool not ready: {e}")
except DatabaseError as e:
    print(f"Database error: {e}")
```

## Configuration

### Default Settings

```python
MIN_POOL_SIZE = 10
MAX_POOL_SIZE = 20
CONNECTION_TIMEOUT = 30.0  # seconds
COMMAND_TIMEOUT = 5.0      # seconds
```

### Custom Configuration

Modify `DatabaseConfig` class in `connection.py`:

```python
class DatabaseConfig:
    MIN_POOL_SIZE = 5
    MAX_POOL_SIZE = 50
    CONNECTION_TIMEOUT = 60.0
    # ...
```

## FastAPI Integration

### Lifespan Management

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.db import init_db, close_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()

app = FastAPI(lifespan=lifespan)
```

### Health Check Endpoint

```python
from fastapi import FastAPI
from backend.db import health_check

app = FastAPI()

@app.get("/health/database")
async def database_health():
    return await health_check()
```

### Query Endpoint Example

```python
from fastapi import FastAPI, HTTPException
from backend.db import fetch_all, QueryError

app = FastAPI()

@app.get("/properties")
async def get_properties():
    try:
        properties = await fetch_all("SELECT * FROM properties LIMIT 100")
        return {"properties": [dict(p) for p in properties]}
    except QueryError as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Testing

Run the test suite:

```bash
python -m backend.db.connection
```

This will test:
- Connection pool initialization
- Query execution (fetch_val, fetch_one, fetch_all)
- Health checks
- INSERT/UPDATE operations
- Graceful shutdown

## Logging

The module uses Python's `logging` module:

```python
import logging

# Set log level
logging.getLogger('backend.db').setLevel(logging.DEBUG)

# Example log output:
# 2025-10-12 10:30:45 - backend.db.connection - INFO - ✅ Database connected successfully in 0.15s
# 2025-10-12 10:30:45 - backend.db.connection - DEBUG - Query executed in 0.003s: SELECT * FROM properties
```

## Performance Tips

1. **Use Connection Pool**: Always use the pool, don't create ad-hoc connections
2. **Parameterized Queries**: Use $1, $2 syntax to prevent SQL injection and enable query caching
3. **Batch Operations**: Use `executemany` for bulk inserts
4. **Monitor Pool**: Check `pool_active` in health_check to detect connection leaks
5. **Set Timeouts**: Use timeout parameter for long-running queries

## Security

- ✅ SSL support in production (set `ENVIRONMENT=production`)
- ✅ Parameterized queries prevent SQL injection
- ✅ Password not logged or exposed
- ✅ Connection timeouts prevent hanging
- ✅ Graceful error messages (no sensitive data)

## Troubleshooting

### "Connection failed"
- Check PostgreSQL is running: `psql -U postgres`
- Verify environment variables
- Check firewall/network settings
- Verify database exists: `psql -U postgres -l`

### "Pool not initialized"
- Call `await init_db()` before using query functions
- Check for errors during initialization

### "Query timeout"
- Increase `COMMAND_TIMEOUT`
- Optimize slow queries
- Check database indices

### "Too many connections"
- Reduce `MAX_POOL_SIZE`
- Check for connection leaks (always use context managers)
- Monitor `pool_active` in health_check

## License

REIMS - Real Estate Intelligence Management System
© 2025 REIMS Development Team

















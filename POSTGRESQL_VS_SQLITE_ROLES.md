# PostgreSQL vs SQLite - Roles and Responsibilities in REIMS

## 🎯 What Each Database Is SUPPOSED To Do

### PostgreSQL (Enterprise Database Server)

**Type:** Client-Server Database
**Location:** Docker container `reims-postgres`
**Port:** 5432

#### Intended Responsibilities:

1. **Primary Data Storage** (Production)
   - Store all document metadata
   - Manage user accounts and permissions
   - Track file processing status
   - Store analytics and metrics

2. **Concurrent Access**
   - Handle multiple users simultaneously
   - Process 100+ requests per second
   - Manage database connections efficiently
   - Transaction isolation for data consistency

3. **Advanced Features**
   ```sql
   -- Complex queries
   SELECT p.name, COUNT(fd.id) as doc_count,
          AVG(fd.file_size) as avg_size
   FROM properties p
   LEFT JOIN financial_documents fd ON fd.property_id = p.id
   GROUP BY p.name
   HAVING COUNT(fd.id) > 10;
   
   -- Full-text search
   SELECT * FROM documents 
   WHERE to_tsvector('english', content) @@ to_tsquery('real estate');
   
   -- Window functions
   SELECT *, 
          ROW_NUMBER() OVER (PARTITION BY property_id ORDER BY upload_date DESC)
   FROM financial_documents;
   ```

4. **Data Integrity**
   - Foreign key constraints
   - Triggers for automatic updates
   - Row-level security
   - ACID compliance

5. **Scalability**
   - Replication (master-slave)
   - Partitioning large tables
   - Connection pooling
   - Backup and recovery

#### PostgreSQL Code Configuration:

**File: `backend/db/connection.py`**
```python
# Async PostgreSQL connection pool
class DatabaseConfig:
    HOST = 'localhost'
    PORT = 5432
    DATABASE = 'reims'
    USER = 'postgres'
    PASSWORD = 'dev123'
    MIN_POOL_SIZE = 10  # Keep 10 connections ready
    MAX_POOL_SIZE = 20  # Allow up to 20 concurrent connections

async def init_db():
    """Create connection pool for PostgreSQL"""
    global _connection_pool
    _connection_pool = await asyncpg.create_pool(
        host=DatabaseConfig.HOST,
        port=DatabaseConfig.PORT,
        database=DatabaseConfig.DATABASE,
        user=DatabaseConfig.USER,
        password=DatabaseConfig.PASSWORD,
        min_size=DatabaseConfig.MIN_POOL_SIZE,
        max_size=DatabaseConfig.MAX_POOL_SIZE
    )
```

**File: `docker-compose.yml`**
```yaml
postgres:
  image: postgres:16
  container_name: reims-postgres
  environment:
    POSTGRES_DB: reims
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: dev123
  ports:
    - "5432:5432"
  volumes:
    - postgres-data:/var/lib/postgresql/data
```

---

### SQLite (Embedded Database)

**Type:** File-based Database
**Location:** `C:\REIMS\reims.db`
**Size:** ~360 KB (grows with data)

#### Actual Responsibilities (Current):

1. **Development Database** (Actually doing production work!)
   - ✅ Storing all 28 uploaded documents
   - ✅ Managing document metadata
   - ✅ Tracking upload status
   - ✅ Storing user data

2. **Simple Operations**
   ```sql
   -- Single-user CRUD operations
   INSERT INTO financial_documents (id, file_name, status)
   VALUES ('uuid...', 'ESP 2024.pdf', 'queued');
   
   SELECT * FROM financial_documents 
   WHERE property_id = 'xxx' 
   ORDER BY upload_date DESC;
   
   UPDATE financial_documents 
   SET status = 'processed' 
   WHERE id = 'uuid...';
   ```

3. **File-Based Storage**
   - No server required
   - Direct file access
   - Single database file
   - Local transactions

4. **Performance Optimizations**
   ```python
   # WAL mode for better concurrency
   PRAGMA journal_mode=WAL;
   
   # Fast synchronization
   PRAGMA synchronous=NORMAL;
   
   # Memory caching
   PRAGMA cache_size=10000;
   
   # Memory-based temp storage
   PRAGMA temp_store=MEMORY;
   ```

#### SQLite Code Configuration:

**File: `backend/api/database.py`**
```python
from dotenv import load_dotenv
load_dotenv()

# Try to get DATABASE_URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:dev123@localhost:5432/reims"  # Default
)

# Try PostgreSQL first
try:
    if DATABASE_URL.startswith("postgresql://"):
        engine = create_engine(DATABASE_URL)
        with engine.connect():
            pass
        print("Connected to PostgreSQL")  # Never prints!
    else:
        engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False}
        )
        print("Using SQLite database")
        
except Exception as e:
    # PostgreSQL connection fails, fallback to SQLite
    print(f"Database connection failed: {e}")
    print("Falling back to SQLite...")
    DATABASE_URL = "sqlite:///./reims.db"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
```

**File: `backend/database_optimized.py`**
```python
DATABASE_URL = "sqlite:///./reims.db"

# SQLite optimizations
SQLITE_PRAGMAS = {
    "journal_mode": "WAL",       # Write-Ahead Logging
    "synchronous": "NORMAL",     # Faster writes
    "cache_size": 10000,         # 10MB cache
    "temp_store": "MEMORY",      # In-memory temp tables
    "mmap_size": 268435456,      # 256MB memory-mapped
}
```

---

## 🔄 Current vs Intended Usage

| Feature | PostgreSQL (Intended) | SQLite (Actual) |
|---------|----------------------|-----------------|
| **Connection** | ❌ Should be active | ✅ Is active |
| **Document Storage** | ❌ Should store 28 docs | ✅ Stores 28 docs |
| **Upload Metadata** | ❌ Should track uploads | ✅ Tracks uploads |
| **User Management** | ❌ Should manage users | ✅ Manages users |
| **Query Performance** | ⏩ Fast (server optimized) | 🐌 Slower (file-based) |
| **Concurrent Users** | ✅ 100+ users | ⚠️ 1-5 users max |
| **Scalability** | ✅ Excellent | ⚠️ Limited |
| **Production Ready** | ✅ Yes | ⚠️ For dev only |

---

## 📊 What's In Each Database RIGHT NOW

### PostgreSQL (Docker Container)

**Status:** Running but EMPTY

```sql
-- All tables exist but have 0 records:
reims=# SELECT COUNT(*) FROM documents;
 count 
-------
     0

reims=# SELECT COUNT(*) FROM financial_documents;
 count 
-------
     0

reims=# SELECT COUNT(*) FROM properties;
 count 
-------
     5  -- Only test data
```

**Schema (Ready but unused):**
```
Tables created:
✅ documents
✅ financial_documents (with upload columns we added!)
✅ properties
✅ users
✅ processing_jobs
✅ extracted_data
✅ tenants
✅ leases

Status: All empty except test properties
```

### SQLite (Local File)

**Status:** ACTIVE and FULL

```sql
-- Your actual data:
sqlite> SELECT COUNT(*) FROM financial_documents;
28  -- All your uploads!

sqlite> SELECT file_name, status FROM financial_documents LIMIT 3;
ESP 2024 Income Statement.pdf|queued
ESP 2024 Cash Flow Statement.pdf|queued
ESP 2024 Balance Sheet.pdf|queued

sqlite> SELECT COUNT(*) FROM properties;
127  -- All property data

sqlite> SELECT COUNT(*) FROM users;
3  -- User accounts
```

**Tables (All populated):**
```
✅ documents (legacy)
✅ financial_documents (28 records - YOUR UPLOADS!)
✅ properties (127 records)
✅ users (3 accounts)
✅ processing_jobs (queue data)
✅ extracted_data (processed documents)
✅ financial_transactions
✅ property_documents
... 27 tables total
```

---

## 🔍 How to See What Each Database Is Doing

### Check PostgreSQL (Should have data, doesn't)

```powershell
# Via Docker
$env:PGPASSWORD = "dev123"
docker exec -i reims-postgres psql -U postgres -d reims -c `
  "SELECT COUNT(*) FROM financial_documents;"
# Result: 0

# Via Python (fails to connect!)
python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://postgres:dev123@localhost:5432/reims'); conn = engine.connect(); print('Connected!')"
# Result: ERROR - password authentication failed
```

### Check SQLite (Has all the data)

```powershell
# Via Python script
python show_my_uploads.py
# Result: Shows all 28 documents

# Via direct query
python -c "import sqlite3; conn = sqlite3.connect('reims.db'); print(f'Documents: {conn.execute(\"SELECT COUNT(*) FROM financial_documents\").fetchone()[0]}'); conn.close()"
# Result: Documents: 28

# Via API
curl http://localhost:8001/api/documents
# Result: Returns all 28 documents from SQLite
```

---

## 💡 Why This Matters

### Current Impact (Using SQLite)

**Advantages:**
- ✅ Everything works
- ✅ No configuration needed
- ✅ Fast for single user
- ✅ Simple to backup (just copy the file)

**Limitations:**
- ⚠️ Can't handle many concurrent users
- ⚠️ Limited query performance on large datasets
- ⚠️ No built-in replication
- ⚠️ File locking issues with multiple processes

### If PostgreSQL Was Working

**Advantages:**
- ✅ Handle 100+ concurrent users
- ✅ Advanced queries run faster
- ✅ Built-in backup/replication
- ✅ Better security (row-level)
- ✅ Production-grade reliability

**Trade-offs:**
- ⚠️ More complex setup
- ⚠️ Requires server management
- ⚠️ Higher resource usage
- ⚠️ Need proper authentication

---

## 🎯 Bottom Line

### PostgreSQL (Enterprise Database Server)
**What it SHOULD do:**
- Store all production data
- Handle multiple users
- Provide advanced analytics
- Scale to millions of records

**What it's ACTUALLY doing:**
- ❌ Nothing (connection fails)
- ❌ Sitting empty in Docker
- ❌ Not receiving any data

### SQLite (Simple File Database)
**What it SHOULD do:**
- Development and testing
- Temporary data storage
- Simple applications

**What it's ACTUALLY doing:**
- ✅ Storing ALL your uploads (28 docs)
- ✅ Running the entire application
- ✅ Handling all database operations
- ✅ Working perfectly!

**The Reality:**
Your REIMS application is running on SQLite (development database) instead of PostgreSQL (production database), but everything is working fine for development purposes!


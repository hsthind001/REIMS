# REIMS Database Architecture - PostgreSQL vs SQLite

## 🏗️ Architecture Overview

REIMS has a **dual-database architecture** with different parts using different databases:

```
┌─────────────────────────────────────────────────────────────┐
│                    REIMS APPLICATION                        │
└─────────────────────────────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
    ┌───────────────────┐   ┌───────────────────┐
    │   POSTGRESQL      │   │     SQLite        │
    │   (Intended)      │   │   (Actual)        │
    │   Docker          │   │   Local File      │
    └───────────────────┘   └───────────────────┘
```

---

## 📊 Current Database Usage

### 🟢 **WHAT IS CURRENTLY WORKING (SQLite)**

| Component | Database | Location | Purpose |
|-----------|----------|----------|---------|
| **Backend API** | SQLite | `C:\REIMS\reims.db` | Document uploads, metadata |
| **File Uploads** | SQLite | `C:\REIMS\reims.db` | Upload tracking |
| **Document Management** | SQLite | `C:\REIMS\reims.db` | File metadata |
| **Queue Service** | SQLite | `queue_service\reims.db` | Job queue (separate) |

### 🟡 **WHAT SHOULD BE USED (PostgreSQL - Not Working)**

| Component | Intended Database | Actual Status | Why Not Working |
|-----------|-------------------|---------------|-----------------|
| **Backend API** | PostgreSQL (Docker) | ❌ Falls back to SQLite | Auth error from Windows |
| **Advanced Queries** | PostgreSQL | ❌ Not used | Connection fails |
| **Production Data** | PostgreSQL | ❌ Not used | Can't connect from host |

---

## 🔍 Detailed Breakdown

### 1️⃣ **SQLite Usage - CURRENTLY ACTIVE**

#### Location
```
C:\REIMS\reims.db (360 KB)
C:\REIMS\backend\reims.db (69 KB - old)
C:\REIMS\queue_service\reims.db (61 KB - separate service)
```

#### Used By
- **Backend API** (`backend/api/database.py`)
- **Upload endpoint** (`backend/api/routes/documents.py`)
- **Document management** (all CRUD operations)

#### What SQLite Stores

**Main Database (`C:\REIMS\reims.db`):**
```sql
-- Tables in SQLite:
- documents (general documents)
- financial_documents (28 records - your uploads!)
- properties (property data)
- users (user accounts)
- processing_jobs (document processing queue)
- extracted_data (processed document data)
- financial_transactions
- property_documents
```

**Your Upload Data Example:**
```
Table: financial_documents
Records: 28 documents

Sample:
┌──────────────────────────────────────┬───────────────────────┬──────────────────┐
│ ID                                   │ File Name             │ Status           │
├──────────────────────────────────────┼───────────────────────┼──────────────────┤
│ 229db006-3257-4921-975b-de3d0ac1bfea │ pg_verify_*.csv       │ queued           │
│ c9d4e907-8591-4157-a235-448eef8e7c1d │ ESP 2024 Income.pdf   │ queued           │
│ d25b77bd-8c4b-4dfe-8e64-87a33363de80 │ ESP 2024 Cash Flow... │ queued           │
└──────────────────────────────────────┴───────────────────────┴──────────────────┘
```

#### Code Using SQLite

**File:** `backend/api/database.py`
```python
# Line 12-36: Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./reims.db")

try:
    if DATABASE_URL.startswith("postgresql://"):
        engine = create_engine(DATABASE_URL)
        # Test connection
        with engine.connect():
            pass
        print("Connected to PostgreSQL")  # ❌ FAILS
    else:
        # ✅ THIS PATH IS TAKEN
        engine = create_engine(
            DATABASE_URL, 
            connect_args={"check_same_thread": False}
        )
        print("Using SQLite database")
except Exception as e:
    # ✅ OR THIS PATH (fallback)
    print(f"Database connection failed: {e}")
    print("Falling back to SQLite...")
    DATABASE_URL = "sqlite:///./reims.db"
    engine = create_engine(DATABASE_URL, ...)
```

**File:** `backend/api/routes/documents.py` (Upload Handler)
```python
# Line 17: Import database connection
from backend.api.database import get_db

# Line 56: Uses SQLAlchemy session (connected to SQLite!)
async def upload_document(
    file: UploadFile = File(...),
    property_id: str = Form(...),
    document_type: str = Form(...),
    db: Session = Depends(get_db)  # ← This gets SQLite connection
):
    # Line 129-156: INSERT into database
    db.execute(text("""
        INSERT INTO financial_documents (
            id, property_id, file_path, file_name, 
            document_type, status, upload_date
        ) VALUES (...)
    """))
    db.commit()  # ← Saves to SQLite!
```

---

### 2️⃣ **PostgreSQL Usage - INTENDED BUT NOT WORKING**

#### Location
```
Docker Container: reims-postgres
Host: localhost (or 127.0.0.1)
Port: 5432
Database: reims
User: postgres
Password: dev123
```

#### Should Be Used For
- **Production data storage**
- **Advanced queries**
- **Concurrent access**
- **Scalability**

#### What PostgreSQL Contains

**Schema (created and ready):**
```sql
-- Tables in PostgreSQL (all empty!):
- documents (0 records)
- financial_documents (0 records - but has upload columns now!)
- properties (some test data)
- users (admin accounts)
- processing_jobs (0 records)
- extracted_data (0 records)
- tenants
- leases
```

**PostgreSQL is Ready But Unused:**
```
✅ Docker container running
✅ Database 'reims' exists
✅ Tables created
✅ Schema matches code
❌ Backend can't connect from Windows
❌ All tables empty (0 records)
```

#### Why PostgreSQL Is NOT Being Used

**Error When Connecting:**
```
psycopg2.OperationalError: 
  connection to server at "localhost" (::1), port 5432 failed: 
  FATAL: password authentication failed for user "postgres"
```

**The Problem:**
1. ✅ Docker exec (inside container) works: `docker exec -it reims-postgres psql -U postgres`
2. ❌ Python from Windows fails: `psycopg2.connect('postgresql://postgres:dev123@...')`
3. **Root Cause:** PostgreSQL `pg_hba.conf` not configured for host connections

**Configuration Needed:**
```bash
# PostgreSQL needs this in pg_hba.conf:
host    all    all    0.0.0.0/0    md5

# Current setting only allows:
local   all    all              trust   # Unix socket only
host    all    all    127.0.0.1/32  md5  # localhost IPv4
host    all    all    ::1/128       md5  # localhost IPv6 (blocked on Windows)
```

#### Code Trying to Use PostgreSQL

**File:** `backend/db/connection.py`
```python
# Line 56-77: PostgreSQL Configuration Class
class DatabaseConfig:
    HOST = os.getenv('DATABASE_HOST', 'localhost')
    PORT = int(os.getenv('DATABASE_PORT', '5432'))
    DATABASE = os.getenv('DATABASE_NAME', 'reims')
    USER = os.getenv('DATABASE_USER', 'postgres')
    PASSWORD = os.getenv('DATABASE_PASSWORD', '')  # ← Empty!
    
    @classmethod
    def get_dsn(cls) -> str:
        return f"postgresql://{cls.USER}:{cls.PASSWORD}@{cls.HOST}:{cls.PORT}/{cls.DATABASE}"

# Line 92-105: Initialize PostgreSQL Pool
async def init_db() -> None:
    global _connection_pool
    _connection_pool = await asyncpg.create_pool(
        host=DatabaseConfig.HOST,
        port=DatabaseConfig.PORT,
        database=DatabaseConfig.DATABASE,
        user=DatabaseConfig.USER,
        password=DatabaseConfig.PASSWORD,  # ❌ Connection fails here
        min_size=DatabaseConfig.MIN_POOL_SIZE,
        max_size=DatabaseConfig.MAX_POOL_SIZE
    )
```

**File:** `.env`
```env
# PostgreSQL configuration (correct password!)
DATABASE_URL=postgresql://postgres:dev123@localhost:5432/reims
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=reims
DATABASE_USER=postgres
DATABASE_PASSWORD=dev123
```

---

## 🔄 Current Data Flow

### When You Upload a File

```
┌──────────┐
│ Frontend │ → POST /api/documents/upload
│ (React)  │
└─────┬────┘
      │
      ▼
┌─────────────────────────────────────────────────┐
│ Backend API (FastAPI)                           │
│ File: backend/api/routes/documents.py           │
│                                                  │
│ 1. Receive file + metadata                      │
│ 2. Upload file to MinIO ✅                       │
│ 3. Try PostgreSQL → FAIL ❌                      │
│ 4. Fallback to SQLite ✅                         │
│ 5. INSERT INTO financial_documents              │
└─────────────┬───────────────────────────────────┘
              │
    ┌─────────┴─────────┐
    │                   │
    ▼                   ▼
┌────────┐      ┌─────────────┐
│ MinIO  │      │   SQLite    │
│ Bucket │      │  reims.db   │
│        │      │             │
│ Files  │      │ Metadata:   │
│ ✅ PDF │      │ ✅ ID       │
│ ✅ CSV │      │ ✅ filename │
│ ✅ XLS │      │ ✅ status   │
└────────┘      │ ✅ date     │
                └─────────────┘
```

### PostgreSQL (Should Be Used But Isn't)

```
┌────────────────────┐
│  PostgreSQL        │
│  (Docker)          │
│                    │
│  Status:           │
│  ✅ Running        │
│  ✅ Accessible     │
│  ✅ Schema ready   │
│  ❌ Empty tables   │
│  ❌ No data        │
│                    │
│  Why unused?       │
│  Connection fails  │
│  from Windows host │
└────────────────────┘
```

---

## 🎯 Summary Table

| Aspect | PostgreSQL | SQLite |
|--------|-----------|---------|
| **Status** | ❌ Configured but not connected | ✅ Working |
| **Location** | Docker container `reims-postgres` | `C:\REIMS\reims.db` |
| **Port** | 5432 | N/A (file-based) |
| **Your Data** | 0 records (empty) | 28 records (all your uploads!) |
| **Connection** | ❌ Fails from Windows | ✅ Works perfectly |
| **Used By** | Nothing currently | All upload/document operations |
| **Purpose** | Production/scalable database | Development fallback |
| **File Storage** | N/A | Local filesystem |
| **Current Role** | Standby (unused) | Primary database |

---

## 🛠️ What Each Database Does

### SQLite (Currently Active)

**Purpose:** Single-file relational database
- ✅ **Stores:** All your uploaded document metadata
- ✅ **Handles:** CRUD operations for documents, properties, users
- ✅ **Location:** Local filesystem (`reims.db`)
- ✅ **Access:** Direct file access, no server needed
- ✅ **Performance:** Fast for single-user/development
- ⚠️ **Limitation:** Not ideal for concurrent users

**What It's Doing Right Now:**
```python
# Every time you upload:
1. Receive file from frontend
2. Save file to MinIO → ✅ Success
3. Save metadata to SQLite → ✅ Success
   INSERT INTO financial_documents VALUES (
     id='229db006...',
     file_name='ESP 2024 Income.pdf',
     status='queued',
     upload_date='2025-10-13 13:10:17'
   )
```

### PostgreSQL (Intended for Production)

**Purpose:** Enterprise-grade relational database server
- ⏳ **Should Store:** All production data
- ⏳ **Should Handle:** Multiple concurrent users
- ⏳ **Should Provide:** Advanced queries, transactions, replication
- ❌ **Currently:** Running but empty, no connections from app
- ❌ **Issue:** Authentication configuration problem

**What It Should Be Doing:**
```python
# What PostgreSQL is designed for:
1. Handle 100+ concurrent users
2. Advanced analytics queries
3. Data backup/replication
4. Row-level security
5. Full-text search
6. Scalability for production
```

---

## 📝 Recommendation

### For Development (Current State)
✅ **Continue using SQLite** - It's working perfectly!

### For Production (Future)
🔧 **Fix PostgreSQL connection** then migrate data:
1. Fix `pg_hba.conf` in Docker
2. Update environment variables
3. Migrate data from SQLite to PostgreSQL
4. Switch DATABASE_URL in `.env`

---

## 🔍 How to Verify Which Database You're Using

**Check backend logs:**
```powershell
# Look for this message when backend starts:
"Using SQLite database"  ← Currently seeing this
# OR
"Connected to PostgreSQL" ← Should see this (but don't)
```

**Check data location:**
```powershell
# SQLite (current):
python show_my_uploads.py  # Shows 28 records

# PostgreSQL (empty):
docker exec -it reims-postgres psql -U postgres -d reims -c "SELECT COUNT(*) FROM financial_documents;"
# Result: 0 rows
```

---

## 💡 Bottom Line

**PostgreSQL:** 
- Enterprise database server
- Intended for production
- Running in Docker but **NOT CONNECTED**
- Currently **EMPTY** (0 records)

**SQLite:**
- Simple file-based database  
- Fallback for development
- **ACTIVELY BEING USED**
- Contains **ALL YOUR DATA** (28 records)

**Your uploads ARE working** - they're just going to SQLite instead of PostgreSQL!


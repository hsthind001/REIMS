# REIMS Support Team Troubleshooting Guide

## 🚨 Critical Issues Analysis

Based on our implementation experience, this guide covers all major issues encountered and their solutions.

## 📋 Issue Categories

### 1. Import/Dependency Issues
### 2. Database Connectivity Problems
### 3. Pydantic/FastAPI Configuration Issues
### 4. Frontend Build and Runtime Issues
### 5. Storage Service Problems
### 6. Queue Management Issues
### 7. Performance and Optimization Issues

---

## 🔧 Critical Import and Dependency Issues

### Issue #1: SQLAlchemy Decimal Import Error

#### Error Message
```
cannot import name 'Decimal' from 'sqlalchemy'
```

#### Root Cause
- SQLAlchemy versions 2.0+ moved `Decimal` type to different module
- Property models were importing from incorrect location

#### Solution
```python
# WRONG (old SQLAlchemy)
from sqlalchemy import Decimal

# CORRECT (SQLAlchemy 2.0+)
from sqlalchemy.types import DECIMAL
from decimal import Decimal  # For Python decimal operations
```

#### Implementation Fix
1. Update all model files to use `DECIMAL` from `sqlalchemy.types`
2. Keep `decimal.Decimal` for Python value operations
3. Alternative: Use `float` type for simpler compatibility

#### Files Affected
- `backend/models/property_models.py`
- `backend/api/property_management.py`

#### Prevention
- Pin SQLAlchemy version in requirements.txt
- Use proper type imports based on SQLAlchemy version
- Implement compatibility layers for different versions

### Issue #2: Missing Python Dependencies

#### Error Messages
```
ModuleNotFoundError: No module named 'pandas'
ModuleNotFoundError: No module named 'minio'
ModuleNotFoundError: No module named 'httpx'
```

#### Root Cause
- Dependencies not installed or incomplete installation
- Virtual environment not activated
- Package versions incompatible

#### Solution - Automated Detection
```python
def check_dependencies():
    required_packages = [
        'fastapi', 'uvicorn', 'sqlalchemy', 'pandas', 
        'pymupdf', 'requests', 'httpx', 'minio', 'python-dotenv'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"Installing missing packages: {missing}")
        subprocess.run([sys.executable, "-m", "pip", "install"] + missing)
```

#### Manual Installation
```bash
# Install all required packages
python -m pip install sqlalchemy fastapi uvicorn pandas pymupdf requests httpx minio python-dotenv

# For development
python -m pip install pytest black flake8
```

#### Prevention
- Create comprehensive requirements.txt
- Use virtual environments
- Implement dependency checking in startup scripts
- Document exact version requirements

### Issue #3: Pydantic Configuration Errors

#### Error Messages
```
pydantic._internal._model_construction.py - KeyboardInterrupt
pydantic core_schema.py - model_field error
```

#### Root Cause
- Pydantic v2 compatibility issues with complex types
- `Decimal` type not properly configured for Pydantic
- Circular imports in model definitions

#### Solution - Simplified Types
```python
# PROBLEMATIC
from decimal import Decimal
class PropertyBase(BaseModel):
    monthly_rent: Decimal

# FIXED
class PropertyBase(BaseModel):
    monthly_rent: float  # Simpler, more compatible
```

#### Advanced Solution - Proper Configuration
```python
from pydantic import BaseModel, ConfigDict
from decimal import Decimal

class PropertyBase(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={Decimal: float}
    )
    monthly_rent: Decimal
```

#### Prevention
- Use simple types (float, int, str) when possible
- Test Pydantic models in isolation
- Implement proper model configuration
- Keep models simple and focused

---

## 🗄️ Database Connectivity Issues

### Issue #4: PostgreSQL Connection Failures

#### Error Message
```
psycopg2.OperationalError: connection to server at "localhost" (::1), 
port 5432 failed: FATAL: password authentication failed for user "postgres"
```

#### Root Cause
- PostgreSQL not installed or not running
- Incorrect connection credentials
- Database configuration mismatch

#### Solution - Graceful Fallback
```python
def get_database_url():
    try:
        # Try PostgreSQL first
        return "postgresql://postgres:password@localhost:5432/reims"
    except Exception:
        # Fallback to SQLite
        logger.warning("PostgreSQL connection failed. Falling back to SQLite...")
        return "sqlite:///./reims.db"
```

#### Implementation
```python
# In database.py
try:
    engine = create_engine(get_postgresql_url())
    engine.connect()  # Test connection
except Exception as e:
    logger.warning(f"PostgreSQL failed: {e}")
    engine = create_engine("sqlite:///./reims.db")
```

#### Prevention
- Always implement database fallbacks
- Use environment variables for database config
- Test database connections on startup
- Document database setup requirements

### Issue #5: SQLite Optimization

#### Performance Issues
- Slow queries on large datasets
- Concurrent access problems
- Missing indexes

#### Solution - SQLite Optimization
```python
# Optimized SQLite configuration
engine = create_engine(
    "sqlite:///./reims.db",
    connect_args={
        "check_same_thread": False,
        "timeout": 20
    },
    pool_pre_ping=True
)

# Apply SQLite pragmas for performance
def setup_sqlite_pragmas(connection):
    connection.execute("PRAGMA foreign_keys=ON")
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA synchronous=NORMAL")
    connection.execute("PRAGMA cache_size=10000")
    connection.execute("PRAGMA temp_store=MEMORY")
```

#### Prevention
- Configure SQLite for production use
- Implement proper indexing strategy
- Use connection pooling
- Monitor query performance

---

## 🖥️ Frontend Build and Runtime Issues

### Issue #6: Node.js Build Failures

#### Error Messages
```
npm ERR! enoent Could not read package.json
Error: The directory "dist" does not exist. Did you build your project?
```

#### Root Cause
- Missing package.json in correct directory
- Build process not completed
- Dependency installation incomplete

#### Solution - Proper Build Process
```bash
# Navigate to correct directory
cd C:\REIMS\frontend

# Clean installation
Remove-Item -Path node_modules -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path package-lock.json -Force -ErrorAction SilentlyContinue

# Fresh install
npm install

# Development server
npm run dev

# Production build
npm run build
npm run start
```

#### Prevention
- Verify working directory before npm commands
- Use full paths in build scripts
- Implement build verification steps
- Document build requirements

### Issue #7: Port Conflicts

#### Error Messages
```
Port 5173 is in use, trying another one...
Port 5174 is in use, trying another one...
```

#### Root Cause
- Multiple development servers running
- Other applications using same ports
- Previous processes not properly terminated

#### Solution - Port Management
```bash
# Check what's using the port
netstat -ano | findstr :5173

# Kill specific process
taskkill /PID <process_id> /F

# Use different port
npm run dev -- --port 5175
```

#### Automated Solution
```json
// In vite.config.js
export default {
  server: {
    port: 5175,
    strictPort: false  // Try next available port
  }
}
```

#### Prevention
- Use port detection in startup scripts
- Implement graceful port selection
- Document port usage
- Clean up processes on shutdown

---

## 🔄 Queue and Background Processing Issues

### Issue #8: Queue Service Failures

#### Error Messages
```
Connection refused to queue service
Queue worker not responding
Background job timeout
```

#### Root Cause
- Queue service not started
- Redis/queue backend not running
- Worker processes crashed

#### Solution - Queue Health Monitoring
```python
def check_queue_health():
    try:
        # Test queue connection
        queue_client = QueueClient()
        queue_client.ping()
        return True
    except Exception as e:
        logger.error(f"Queue health check failed: {e}")
        return False

def start_queue_with_fallback():
    if not check_queue_health():
        logger.warning("Starting fallback queue processing")
        # Use in-memory processing or database queue
        return InMemoryQueue()
    return RedisQueue()
```

#### Prevention
- Implement queue health checks
- Use fallback processing methods
- Monitor queue performance
- Set up alerting for queue failures

---

## ⚡ Performance and Optimization Issues

### Issue #9: Slow API Response Times

#### Symptoms
- API calls taking >5 seconds
- Frontend timeouts
- Poor user experience

#### Root Cause
- Inefficient database queries
- Missing database indexes
- Large file processing blocking requests

#### Solution - Performance Optimization
```python
# Add database indexes
class Property(Base):
    __tablename__ = "properties"
    
    property_code = Column(String, index=True)  # Add indexes
    city = Column(String, index=True)
    state = Column(String, index=True)

# Optimize queries
def get_properties_optimized(db: Session, limit: int = 100):
    return db.query(Property)\
             .options(selectinload(Property.tenants))\
             .limit(limit)\
             .all()

# Use background processing for heavy tasks
@router.post("/process-document")
async def process_document_async(document_id: int):
    # Queue the processing instead of blocking
    job = queue.enqueue(process_document, document_id)
    return {"job_id": job.id, "status": "queued"}
```

#### Prevention
- Profile API performance regularly
- Use database query analysis tools
- Implement caching strategies
- Monitor response times

### Issue #10: Memory Usage Issues

#### Symptoms
- High memory consumption
- Application crashes
- Slow performance over time

#### Root Cause
- Memory leaks in file processing
- Large files loaded into memory
- Database connections not closed

#### Solution - Memory Management
```python
# Stream large file processing
def process_large_file(file_path):
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(8192)  # Process in chunks
            if not chunk:
                break
            process_chunk(chunk)

# Proper resource cleanup
@contextmanager
def get_db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

# Monitor memory usage
import psutil
def check_memory_usage():
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    if memory_mb > 1000:  # Alert if over 1GB
        logger.warning(f"High memory usage: {memory_mb:.2f}MB")
```

#### Prevention
- Implement memory monitoring
- Use streaming for large files
- Profile memory usage patterns
- Set memory limits and alerts

---

## 🛠️ Quick Fix Commands

### Emergency System Recovery
```bash
# Stop all processes
Stop-Process -Name "python" -Force -ErrorAction SilentlyContinue
Stop-Process -Name "node" -Force -ErrorAction SilentlyContinue
Stop-Process -Name "minio" -Force -ErrorAction SilentlyContinue

# Clean restart
cd C:\REIMS
python start_optimized_server.py

# Frontend restart
cd C:\REIMS\frontend
npm run dev
```

### Database Recovery
```bash
# Backup current database
Copy-Item "reims.db" "reims.db.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"

# Reset database (if needed)
Remove-Item "reims.db" -Force
python migrate_database.py
```

### Dependency Reinstall
```bash
# Python dependencies
python -m pip uninstall -y sqlalchemy fastapi uvicorn pandas pymupdf requests httpx minio python-dotenv
python -m pip install sqlalchemy fastapi uvicorn pandas pymupdf requests httpx minio python-dotenv

# Node.js dependencies
cd frontend
Remove-Item -Path node_modules -Recurse -Force
Remove-Item -Path package-lock.json -Force
npm install
```

---

## 📊 Monitoring and Alerting

### Health Check Endpoints
```bash
# Backend health
curl http://localhost:8000/health

# Service-specific health
curl http://localhost:8000/analytics/health
curl http://localhost:8000/queue/health
curl http://localhost:8000/storage/health
```

### Log Analysis
```bash
# Check for errors in logs
python start_optimized_server.py 2>&1 | findstr "ERROR"

# Monitor specific issues
python start_optimized_server.py 2>&1 | findstr "Failed\|Error\|Exception"
```

### Performance Monitoring
```python
# Simple performance monitor
import time
import psutil

def monitor_system():
    while True:
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        print(f"CPU: {cpu}%, Memory: {memory}%")
        time.sleep(30)
```

---

## 📞 Escalation Procedures

### Level 1 - Self-Service
1. Check system health endpoints
2. Restart services using quick fix commands
3. Review recent changes or updates
4. Check resource usage (CPU, memory, disk)

### Level 2 - Technical Support
1. Collect error logs and symptoms
2. Document steps to reproduce issue
3. Check for known issues in this guide
4. Implement workarounds if available

### Level 3 - Development Team
1. Provide detailed error analysis
2. Include system configuration details
3. Share relevant code sections
4. Propose long-term solutions

### Emergency Contacts
- **System Administrator**: Primary escalation
- **Database Administrator**: Database issues
- **Development Team**: Code-related problems
- **Infrastructure Team**: Server and network issues

---

## 📚 Documentation Updates

### When to Update This Guide
- New error patterns discovered
- Solutions tested and verified
- System configuration changes
- Version updates or migrations

### How to Update
1. Document new issues with exact error messages
2. Provide step-by-step solutions
3. Include prevention strategies
4. Test solutions in development environment
5. Update relevant sections of this guide

### Version Control
- Keep this document under version control
- Track changes and updates
- Maintain change log
- Regular reviews and updates
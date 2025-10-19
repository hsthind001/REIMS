# REIMS Database Credentials

## PostgreSQL Connection Details

### Basic Information
- **Host:** localhost
- **Port:** 5432
- **Database:** reims
- **Username:** postgres
- **Password:** dev123

### Connection URLs

#### Standard PostgreSQL URL
```
postgresql://postgres:dev123@localhost:5432/reims
```

#### JDBC URL (Java applications)
```
jdbc:postgresql://localhost:5432/reims?user=postgres&password=dev123
```

#### SQLAlchemy URL (Python)
```python
DATABASE_URL = "postgresql://postgres:dev123@localhost:5432/reims"
```

#### Connection String (Node.js)
```javascript
const connectionString = 'postgresql://postgres:dev123@localhost:5432/reims'
```

---

## Connecting with Different Tools

### 1. psql (Command Line)
```bash
psql -h localhost -p 5432 -U postgres -d reims
# When prompted, enter password: dev123
```

Or with password in environment:
```bash
export PGPASSWORD=dev123
psql -h localhost -p 5432 -U postgres -d reims
```

### 2. pgAdmin
1. Add New Server
2. General Tab:
   - Name: REIMS Local
3. Connection Tab:
   - Host: localhost
   - Port: 5432
   - Database: reims
   - Username: postgres
   - Password: dev123

### 3. DBeaver
1. New Database Connection → PostgreSQL
2. Enter:
   - Host: localhost
   - Port: 5432
   - Database: reims
   - Username: postgres
   - Password: dev123
3. Test Connection → Finish

### 4. DataGrip / IntelliJ
1. Database Tool Window → + → Data Source → PostgreSQL
2. Enter connection details above
3. Test Connection

### 5. Python (psycopg2)
```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="reims",
    user="postgres",
    password="dev123"
)
cursor = conn.cursor()
cursor.execute("SELECT version()")
print(cursor.fetchone())
```

### 6. Python (SQLAlchemy)
```python
from sqlalchemy import create_engine

engine = create_engine('postgresql://postgres:dev123@localhost:5432/reims')
conn = engine.connect()
result = conn.execute("SELECT * FROM documents LIMIT 5")
for row in result:
    print(row)
```

---

## Database Schema

### Main Tables

#### 1. documents
Stores document metadata
```sql
SELECT * FROM documents;
```

Columns:
- `id` - Document UUID
- `filename` - Original filename
- `property_id` - Related property
- `document_type` - Type of document
- `status` - queued/processing/processed/failed
- `upload_date` - When uploaded
- `file_size` - File size in bytes
- `minio_path` - Path in MinIO storage

#### 2. processed_data
Stores AI processing results
```sql
SELECT * FROM processed_data;
```

Columns:
- `document_id` - FK to documents
- `processing_status` - success/error
- `document_type` - Classified type
- `confidence_score` - AI confidence (0-1)
- `extracted_data` - JSON with extracted fields
- `insights` - JSON with AI insights
- `processing_time_seconds` - Processing duration

#### 3. processing_jobs
Tracks background jobs
```sql
SELECT * FROM processing_jobs;
```

#### 4. properties
Property information
```sql
SELECT * FROM properties;
```

#### 5. financial_documents
Financial document metadata
```sql
SELECT * FROM financial_documents;
```

---

## Useful SQL Queries

### View All Documents
```sql
SELECT id, filename, status, upload_date 
FROM documents 
ORDER BY upload_date DESC 
LIMIT 10;
```

### View Processed Documents with Results
```sql
SELECT 
    d.filename,
    d.status,
    p.document_type,
    p.confidence_score,
    p.processing_time_seconds
FROM documents d
LEFT JOIN processed_data p ON d.id = p.document_id
WHERE d.status = 'processed'
ORDER BY d.upload_date DESC;
```

### View Your Recently Uploaded Documents
```sql
SELECT 
    id,
    filename,
    status,
    document_type,
    TO_CHAR(upload_date, 'YYYY-MM-DD HH24:MI:SS') as uploaded_at
FROM documents 
WHERE id IN (
    '0f134780-2dfb-4f14-9387-1e1112601d8f',
    '2c34fa2c-cf24-4bbb-b9ad-4af92cde13e6',
    '59f4550c-5686-4ba9-9df1-51a7c436e4c2'
);
```

### Get AI Extracted Data
```sql
SELECT 
    d.filename,
    p.extracted_data::json->>'financial_metrics' as financial_data,
    p.insights::json->>'summary' as summary
FROM documents d
JOIN processed_data p ON d.id = p.document_id
WHERE d.id = '2c34fa2c-cf24-4bbb-b9ad-4af92cde13e6';
```

### Processing Statistics
```sql
SELECT 
    status,
    COUNT(*) as count,
    ROUND(AVG(file_size)/1024/1024, 2) as avg_size_mb
FROM documents
GROUP BY status;
```

---

## Quick Commands

### List all tables
```sql
\dt
-- or
SELECT tablename FROM pg_tables WHERE schemaname = 'public';
```

### Describe table structure
```sql
\d documents
-- or
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'documents';
```

### Count documents by status
```sql
SELECT status, COUNT(*) 
FROM documents 
GROUP BY status;
```

### View latest 5 uploads
```sql
SELECT filename, status, upload_date
FROM documents
ORDER BY upload_date DESC
LIMIT 5;
```

---

## Backup & Restore

### Backup Database
```bash
pg_dump -h localhost -p 5432 -U postgres -d reims > reims_backup.sql
```

### Restore Database
```bash
psql -h localhost -p 5432 -U postgres -d reims < reims_backup.sql
```

---

## Other Service Credentials

### MinIO (Object Storage)
- **URL:** http://localhost:9001
- **Username:** minioadmin
- **Password:** minioadmin
- **API Endpoint:** http://localhost:9000

### Grafana (Monitoring)
- **URL:** http://localhost:3000
- **Username:** admin
- **Password:** admin123

### Redis (Queue)
- **Host:** localhost
- **Port:** 6379
- **No password required**

---

## Environment Variables

Add these to your `.env` file:

```bash
# PostgreSQL
DATABASE_URL=postgresql://postgres:dev123@localhost:5432/reims
DB_HOST=localhost
DB_PORT=5432
DB_NAME=reims
DB_USER=postgres
DB_PASSWORD=dev123

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=reims-documents

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
```

---

## Troubleshooting

### Cannot connect to PostgreSQL
1. Check if container is running:
   ```bash
   docker ps | grep postgres
   ```

2. Check if port is listening:
   ```bash
   netstat -an | grep 5432
   ```

3. Restart container:
   ```bash
   docker restart reims-postgres
   ```

### Permission denied
Make sure you're using the correct password: `dev123`

### Database does not exist
The database `reims` should be created automatically. If not:
```sql
CREATE DATABASE reims;
```

---

**Last Updated:** October 13, 2025
**Docker Container:** reims-postgres
**PostgreSQL Version:** 16















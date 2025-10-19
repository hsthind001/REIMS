# Database Web Access Guide

## 🌐 **3 Ways to View Your Database in a Browser**

---

## **Option 1: pgAdmin (Full Database Management) - NEW!**

### Access URL:
```
http://localhost:5050
```

### Login Credentials:
- **Email:** admin@example.com
- **Password:** admin123

### First-Time Setup (One-Time Only):

1. **Open pgAdmin**
   ```
   http://localhost:5050
   ```

2. **Add Server Connection**
   - Click "Add New Server" (or right-click Servers → Register → Server)

3. **General Tab**
   - Name: `REIMS PostgreSQL`

4. **Connection Tab**
   - Host name/address: `postgres` (or `reims-postgres`)
   - Port: `5432`
   - Maintenance database: `reims`
   - Username: `postgres`
   - Password: `dev123`
   - ✅ Save password: Check this box

5. **Click "Save"**

### Using pgAdmin:

Once connected, you can:
- ✅ Browse all tables visually
- ✅ Run SQL queries
- ✅ View table data in grids
- ✅ Export data to CSV/JSON
- ✅ Create/modify tables
- ✅ View table relationships
- ✅ See indexes and constraints

### Navigate to Your Tables:
```
Servers → REIMS PostgreSQL → Databases → reims → Schemas → public → Tables
```

Right-click any table → View/Edit Data → All Rows

### Your Important Tables:
- **documents** - All uploaded documents
- **processed_data** - AI processing results
- **processing_jobs** - Queue job tracking
- **properties** - Property information
- **financial_documents** - Financial data

---

## **Option 2: REIMS API Docs (Interactive)**

### Access URL:
```
http://localhost:8001/docs
```

### Features:
- ✅ Interactive API testing
- ✅ View all database data as JSON
- ✅ Test queries in browser
- ✅ See API response formats
- ✅ Try out endpoints without code

### Try These Endpoints:

**Get All Documents:**
```
GET /api/documents
```
Click "Try it out" → "Execute" → See your uploaded documents

**Get Document Status:**
```
GET /api/documents/{document_id}/status
```
Enter your document ID → Execute → See processing status and metrics

**Get Document Details:**
```
GET /api/documents/{document_id}
```
See complete document information

---

## **Option 3: Direct JSON Endpoints**

You can also view data directly in your browser:

### View All Documents:
```
http://localhost:8001/api/documents
```

### View Specific Document:
```
http://localhost:8001/api/documents/2c34fa2c-cf24-4bbb-b9ad-4af92cde13e6
```

### View Document Status:
```
http://localhost:8001/api/documents/2c34fa2c-cf24-4bbb-b9ad-4af92cde13e6/status
```

### System Health:
```
http://localhost:8001/health
```

---

## **Comparison: Which One to Use?**

| Feature | pgAdmin | API Docs | Direct JSON |
|---------|---------|----------|-------------|
| Visual table browser | ✅ Best | ❌ | ❌ |
| SQL query editor | ✅ Best | ❌ | ❌ |
| Edit data | ✅ Yes | ❌ | ❌ |
| Easy to use | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| View relationships | ✅ Yes | ❌ | ❌ |
| Export data | ✅ CSV/JSON | 📋 Copy | 📋 Copy |
| Test APIs | ❌ | ✅ Best | ❌ |
| Quick view | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**Recommendation:**
- 📊 **Exploring database tables?** → Use **pgAdmin**
- 🧪 **Testing APIs?** → Use **API Docs**
- ⚡ **Quick data check?** → Use **Direct JSON**

---

## **pgAdmin Quick Start Guide**

### 1. View Your Uploaded Documents

After connecting to the server:

1. Navigate: **Servers → REIMS PostgreSQL → Databases → reims → Schemas → public → Tables → documents**
2. Right-click **documents** → **View/Edit Data** → **All Rows**
3. You'll see a grid with all your documents:
   - `id` - Document UUID
   - `filename` - Original filename
   - `status` - queued/processing/processed
   - `upload_date` - When uploaded
   - `file_size` - Size in bytes

### 2. View AI Processing Results

1. Navigate to: **Tables → processed_data**
2. Right-click → **View/Edit Data** → **All Rows**
3. See AI-extracted data:
   - `document_id` - Links to documents table
   - `document_type` - Classified type
   - `confidence_score` - AI confidence (0-1)
   - `extracted_data` - JSON with financial metrics
   - `insights` - JSON with AI insights

### 3. Run SQL Queries

1. Right-click **reims database** → **Query Tool**
2. Type your SQL:
   ```sql
   SELECT * FROM documents 
   WHERE status = 'processed' 
   ORDER BY upload_date DESC 
   LIMIT 10;
   ```
3. Click **▶ Execute/Refresh** (F5)
4. See results in grid below

### 4. View Your Documents

```sql
-- All your uploaded documents
SELECT 
    id,
    filename,
    status,
    document_type,
    file_size,
    TO_CHAR(upload_date, 'YYYY-MM-DD HH24:MI:SS') as uploaded
FROM documents 
ORDER BY upload_date DESC;
```

### 5. View AI Results with Filenames

```sql
-- Join documents with AI results
SELECT 
    d.filename,
    d.status,
    p.document_type,
    p.confidence_score,
    p.processing_time_seconds,
    p.extracted_data::json->>'financial_metrics' as metrics
FROM documents d
LEFT JOIN processed_data p ON d.id = p.document_id
ORDER BY d.upload_date DESC;
```

---

## **All Your Database Access URLs**

| Service | URL | Credentials |
|---------|-----|-------------|
| **pgAdmin** | http://localhost:5050 | admin@example.com / admin123 |
| **API Docs** | http://localhost:8001/docs | None required |
| **Frontend** | http://localhost:3001 | None required |
| **MinIO Console** | http://localhost:9001 | minioadmin / minioadmin |
| **Grafana** | http://localhost:3000 | admin / admin123 |
| **Prometheus** | http://localhost:9090 | None required |

---

## **PostgreSQL Connection Details (for pgAdmin)**

When adding server in pgAdmin, use these values:

```
Host: postgres (or reims-postgres)
Port: 5432
Database: reims
Username: postgres
Password: dev123
```

**Important:** Use `postgres` as the hostname (not `localhost`) because pgAdmin runs inside Docker and needs to connect to the postgres container.

---

## **Troubleshooting**

### pgAdmin won't connect?

**Try these hostnames in order:**
1. `postgres` (recommended)
2. `reims-postgres` (container name)
3. `host.docker.internal` (Windows/Mac Docker Desktop)
4. `172.17.0.1` (Docker bridge network)

### Can't access pgAdmin?

```bash
# Check if pgAdmin is running
docker ps | grep pgadmin

# View pgAdmin logs
docker logs reims-pgadmin

# Restart pgAdmin
docker restart reims-pgadmin
```

### Forgot password?

```bash
# Reset pgAdmin
docker-compose down pgadmin
docker volume rm reims_pgadmin_data
docker-compose up -d pgadmin
```

---

## **Quick Commands**

### Start/Stop pgAdmin
```bash
# Start
docker-compose up -d pgadmin

# Stop
docker-compose stop pgadmin

# View logs
docker logs -f reims-pgadmin

# Restart
docker restart reims-pgadmin
```

### Check Status
```bash
docker ps | grep pgadmin
```

---

## **Next Steps**

1. ✅ **Open pgAdmin:** http://localhost:5050
2. ✅ **Login:** admin@example.com / admin123
3. ✅ **Add Server:** Use connection details above
4. ✅ **Browse Tables:** Navigate to documents table
5. ✅ **View Your Data:** See your uploaded documents!

**Enjoy visual database browsing!** 🎉


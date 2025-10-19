# REIMS Database - Simple Explanation

## Quick Answer

**You have 2 databases in REIMS:**

1. **PostgreSQL** - Fancy server database (NOT being used)
2. **SQLite** - Simple file database (CURRENTLY being used)

---

## 🔵 PostgreSQL - What Is It?

**Think of it as:** A powerful database server (like MySQL, Oracle)

**Where is it?**
- Running in Docker container called `reims-postgres`
- Accessible on port 5432
- Has username: `postgres`, password: `dev123`

**What is PostgreSQL SUPPOSED to do?**
- Store all your production data
- Handle 100+ users at the same time
- Run fast complex queries
- Backup and replicate data
- Provide enterprise-level security

**What is PostgreSQL ACTUALLY doing?**
- **NOTHING!** 
- It's running but **EMPTY** (0 records in all tables)
- Your app **CAN'T CONNECT** to it from Windows
- Error: "password authentication failed"

**Why can't it connect?**
```
Windows (your app)  →  [X]  →  Docker (PostgreSQL)
       ↓
   Password: dev123
       ↓
   PostgreSQL says: "I don't recognize you!"
   
   Problem: Docker PostgreSQL isn't configured to accept
            connections from Windows host
```

---

## 🟢 SQLite - What Is It?

**Think of it as:** A simple database stored in a single file (like Microsoft Access)

**Where is it?**
- File location: `C:\REIMS\reims.db`
- Just a regular file on your computer (360 KB)
- No server, no port, no network

**What is SQLite SUPPOSED to do?**
- Quick prototyping
- Development and testing
- Small applications
- Single-user apps

**What is SQLite ACTUALLY doing?**
- **EVERYTHING!** 
- Storing ALL 28 of your uploaded documents
- Tracking all file metadata
- Managing all properties (127 records)
- Storing user accounts (3 users)
- **Running your entire application!**

**Why is it working?**
```
Windows (your app)  →  [✓]  →  SQLite file
       ↓
   No password needed
   Direct file access
   
   Result: Works perfectly!
```

---

## 📊 Side-by-Side Comparison

| Feature | PostgreSQL | SQLite |
|---------|-----------|--------|
| **What is it?** | Database server | Database file |
| **Location** | Docker container | C:\REIMS\reims.db |
| **Needs server?** | Yes (port 5432) | No (just a file) |
| **Your uploads** | 0 documents | 28 documents |
| **Connection** | ❌ Fails | ✅ Works |
| **Current role** | Unused | Active |
| **Good for** | 100+ users | 1-5 users |
| **Speed** | Very fast | Fast enough |
| **Setup complexity** | Complex | Simple |

---

## 🔄 What Happens When You Upload a File?

### Current Flow (Using SQLite)

```
1. You upload "ESP 2024 Income.pdf" from frontend
        ↓
2. Backend receives the file
        ↓
3. Backend tries PostgreSQL
   Result: ❌ Can't connect!
        ↓
4. Backend falls back to SQLite
   Result: ✅ Connected!
        ↓
5. File saved to MinIO: ✅
   Metadata saved to SQLite: ✅
        ↓
6. You see file in MinIO console: ✅
   Data is in SQLite database: ✅
```

### What SHOULD Happen (Using PostgreSQL)

```
1. You upload file
        ↓
2. Backend receives file
        ↓
3. Backend connects to PostgreSQL
   Result: ✅ Connected!
        ↓
4. File saved to MinIO: ✅
   Metadata saved to PostgreSQL: ✅
        ↓
5. Multiple users can access simultaneously
   Advanced analytics work faster
   Production-ready setup
```

---

## 📁 Where Is YOUR Data?

### Files (PDFs, CSVs, Excel)
**Location:** MinIO object storage
- Bucket: `reims-files`
- Access: http://localhost:9001
- Status: ✅ All 28 files stored correctly

### Metadata (file info, dates, status)
**Location:** SQLite database
- File: `C:\REIMS\reims.db`
- Table: `financial_documents`
- Records: 28 uploaded documents
- Status: ✅ All data stored correctly

### What's in PostgreSQL?
**Location:** Docker container
- Database: `reims`
- Tables: All created and ready
- Records: **0** (completely empty)
- Status: ⏸️ Waiting to be used

---

## 🎯 So What's the Problem?

**There's NO problem with your data!**

✅ Your 28 files are uploaded
✅ Files are in MinIO
✅ Metadata is in SQLite
✅ Everything is working

**The "issue" is:**
- App uses SQLite (development database)
- Instead of PostgreSQL (production database)
- But functionally, **everything works!**

**For development:** This is perfectly fine!
**For production:** You'd want to fix PostgreSQL connection

---

## 💡 Real-World Analogy

**PostgreSQL** = Industrial warehouse with loading docks, forklifts, multiple workers
- Built for heavy loads
- Can handle many people
- Needs proper setup
- Currently: **Empty, gate locked**

**SQLite** = Your garage at home
- Simple, easy access
- Good for one person
- No setup needed  
- Currently: **Full of your stuff, working great**

**Your situation:**
You meant to use the warehouse (PostgreSQL), but the gate's locked. So you're using your garage (SQLite) instead, and it's working fine for now!

---

## 🔧 How to Check Your Data

### View Your Uploads (SQLite)
```powershell
# Easy way - run the script
python show_my_uploads.py

# API way
curl http://localhost:8001/api/documents

# Direct database way
python -c "import sqlite3; conn = sqlite3.connect('reims.db'); docs = conn.execute('SELECT COUNT(*) FROM financial_documents').fetchone(); print(f'Total docs: {docs[0]}'); conn.close()"
```

### Check PostgreSQL (Empty)
```powershell
# From Windows
docker exec -it reims-postgres psql -U postgres -d reims -c "SELECT COUNT(*) FROM financial_documents;"
# Result: 0

# Why it's empty
docker exec -it reims-postgres psql -U postgres -d reims -c "SELECT * FROM financial_documents;"
# Result: (0 rows)
```

---

## ✅ Conclusion

### PostgreSQL (Production Database)
- **Status:** Configured but not working
- **Data:** None (empty)
- **Role:** Standby, waiting to be connected

### SQLite (Development Database)
- **Status:** Working perfectly
- **Data:** All 28 of your uploads + more
- **Role:** Actively running your application

**Bottom line:** Your app is using SQLite (simple) instead of PostgreSQL (advanced), but **your data is safe and everything works!**


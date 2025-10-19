# 🗄️ How to Access SQLite Database

## 📍 Your Database Location
**File:** `C:\REIMS\reims.db`

---

## 🎯 Method 1: Use Existing Python Scripts (Easiest!)

### Option A: View All Uploads
```bash
python show_my_uploads.py
```
Shows all your uploaded documents in a nice table format.

### Option B: Check Database Details
```bash
python check_database.py
```
Shows detailed information about your database records.

---

## 🎯 Method 2: DB Browser for SQLite (Best GUI Tool - RECOMMENDED!)

### Installation:
1. **Download:** https://sqlitebrowser.org/dl/
2. **Install:** Run the installer (it's free and open-source)
3. **Open:** Launch "DB Browser for SQLite"

### How to Use:
1. Click **"Open Database"**
2. Navigate to `C:\REIMS\reims.db`
3. Click **"Browse Data"** tab
4. Select table from dropdown (e.g., `financial_documents`)
5. View/edit/search your data!

### Features:
✅ Visual table browsing  
✅ SQL query execution  
✅ Data editing  
✅ Export to CSV/JSON  
✅ Database structure visualization  
✅ No coding required!

---

## 🎯 Method 3: SQLite Command Line Tool

### Installation:
1. **Download:** https://www.sqlite.org/download.html
   - Get "sqlite-tools-win32-x86-*.zip"
2. **Extract:** Unzip to a folder (e.g., `C:\sqlite\`)
3. **Add to PATH** (optional) or use full path

### How to Use:
```bash
# Navigate to SQLite folder or use full path
cd C:\sqlite
.\sqlite3.exe C:\REIMS\reims.db

# Once inside SQLite prompt:
.tables                              # List all tables
.schema financial_documents          # Show table structure
SELECT * FROM financial_documents;   # View all records
.exit                                # Exit SQLite
```

### Useful SQLite Commands:
```sql
-- List all tables
.tables

-- Show table structure
.schema financial_documents

-- View all uploaded files
SELECT id, file_name, document_type, status, upload_date 
FROM financial_documents 
ORDER BY upload_date DESC;

-- Count total uploads
SELECT COUNT(*) as total_uploads FROM financial_documents;

-- View by document type
SELECT document_type, COUNT(*) as count 
FROM financial_documents 
GROUP BY document_type;

-- Search for specific file
SELECT * FROM financial_documents 
WHERE file_name LIKE '%yourfile%';

-- Enable column headers and formatted output
.headers on
.mode column

-- Exit
.exit
```

---

## 🎯 Method 4: VS Code Extension (If You Use VS Code)

### Installation:
1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "SQLite Viewer" or "SQLite"
4. Install "SQLite Viewer" by Florian Klampfer

### How to Use:
1. Open VS Code in `C:\REIMS` folder
2. Right-click `reims.db` in file explorer
3. Select "Open Database"
4. Browse tables and data visually

---

## 🎯 Method 5: Create Quick Python Script

I can create a simple interactive script for you:

```python
# quick_db_view.py
import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect('reims.db')

# View all tables
print("\n📊 Available Tables:")
tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
print(tables)

# View financial_documents
print("\n📄 Recent Uploads:")
df = pd.read_sql("""
    SELECT id, file_name, document_type, status, upload_date 
    FROM financial_documents 
    ORDER BY upload_date DESC 
    LIMIT 10
""", conn)
print(df)

conn.close()
```

---

## 🎯 Quick Comparison

| Method | Difficulty | Best For |
|--------|-----------|----------|
| **Python Scripts** | ⭐ Easy | Quick checks |
| **DB Browser** | ⭐ Easy | Visual browsing, editing |
| **SQLite CLI** | ⭐⭐ Medium | Power users, scripts |
| **VS Code Extension** | ⭐ Easy | Developers |

---

## 📋 Common Tasks

### 1. View All Uploaded Files
```bash
# Using Python
python show_my_uploads.py

# Using SQLite CLI
sqlite3 reims.db "SELECT * FROM financial_documents"
```

### 2. Export Data to CSV
```bash
# Using SQLite CLI
sqlite3 reims.db
.headers on
.mode csv
.output my_data.csv
SELECT * FROM financial_documents;
.exit
```

### 3. Check Database Size
```powershell
Get-Item reims.db | Select-Object Name, @{Name="Size(KB)";Expression={[math]::Round($_.Length/1KB,2)}}
```

### 4. Count Records
```bash
sqlite3 reims.db "SELECT COUNT(*) FROM financial_documents"
```

---

## 🎯 My Recommendation

**For beginners/visual users:**
→ Use **DB Browser for SQLite** (download from https://sqlitebrowser.org)

**For quick checks:**
→ Use the Python scripts we already created (`show_my_uploads.py`)

**For automation/scripting:**
→ Use **SQLite command line** tool

**For developers:**
→ Use **VS Code extension**

---

## 📞 Need Help?

If you want me to:
- Create a custom Python script to view specific data
- Write SQL queries for specific reports
- Set up any of these tools
- Export data in a specific format

Just let me know! 🚀

---

## 🔍 Your Current Database

**Location:** `C:\REIMS\reims.db`  
**Size:** ~352 KB  
**Records:** 29 documents uploaded  
**Tables:** financial_documents, properties, tenants, leases, etc.

---

*Last Updated: 2025-10-13*


# 🔧 Fix ESP Files Processing - Step by Step Guide

## 📋 Problem Summary

✅ **What's Working:**
- 19 ESP financial files uploaded successfully
- Files stored in MinIO ✅
- Metadata stored in SQLite database ✅
- Redis is running ✅

❌ **What's NOT Working:**
- Background worker is NOT running
- Files stuck in "queued" status
- No data extraction from PDFs
- Frontend showing hardcoded data

---

## 🎯 The Fix Plan

We'll fix this in 4 steps:

### Step 1: Start the Background Worker ⏰
**Time**: 2 minutes  
**What**: Start the worker to process queued documents

### Step 2: Process Existing Queued Files 📄
**Time**: 5-10 minutes  
**What**: Process all 19 ESP files to extract data

### Step 3: Verify Data Extraction ✅
**Time**: 2 minutes  
**What**: Check that data was extracted to database

### Step 4: Update Frontend to Show Real Data 📊
**Time**: 5 minutes  
**What**: Ensure frontend displays extracted data

---

## 🚀 STEP 1: Start Background Worker

### Option A: Using PowerShell Script (Recommended)

```powershell
# Open a NEW terminal window and run:
.\start_worker.ps1
```

### Option B: Manual Start

```powershell
# Navigate to queue_service directory
cd queue_service

# Start the worker
python worker.py
```

### Expected Output:
```
✅ Worker {worker_id} starting to process queues: ['document_processing', 'ai_analysis', 'notifications']
✅ Redis connection established
⏳ Waiting for jobs...
```

### ⚠️ Keep This Window Open!
The worker must run continuously in the background.

---

## 🔧 STEP 2: Trigger Processing of Queued Files

We have 3 options:

### Option A: Use API Endpoint (Easiest)

```powershell
# In a NEW terminal, run:
curl http://localhost:8001/api/ai-processing/process-all -X POST
```

Expected Response:
```json
{
  "status": "batch_processing_started",
  "documents_queued": 19,
  "message": "Started processing 19 documents"
}
```

### Option B: Create Processing Script

I'll create a script: `process_queued_files.py`

```python
import requests

response = requests.post('http://localhost:8001/api/ai-processing/process-all')
print(response.json())
```

### Option C: Process Manually via Python

```python
# Run in Python
from queue_service.client import QueueClient
import sqlite3

# Get queued documents
conn = sqlite3.connect('reims.db')
cursor = conn.cursor()
cursor.execute("SELECT id, file_path FROM financial_documents WHERE status='queued'")
docs = cursor.fetchall()

# Queue each for processing
client = QueueClient()
for doc_id, file_path in docs:
    job_id = client.enqueue_document(doc_id, {'file_path': file_path})
    print(f"Queued {doc_id} -> Job {job_id}")
```

---

## ✅ STEP 3: Verify Data Extraction

### 3.1 Check Processing Status

```powershell
# Watch the worker terminal
# You should see logs like:
# ✅ Processed document: ESP 2024 Income Statement.pdf
# ✅ Extracted data: {'revenue': 1500000, 'expenses': 800000}
```

### 3.2 Check Database

```powershell
# Run the database viewer
python browse_database.py

# OR use the trace script
python trace_uploaded_files.py
```

### 3.3 Check Extracted Data Table

```powershell
# Quick SQL query
sqlite3 reims.db "SELECT COUNT(*) FROM extracted_data"
# Should show more than 1 record

sqlite3 reims.db "SELECT document_id, data_type FROM extracted_data LIMIT 5"
# Should show your ESP files
```

### 3.4 Verify Financial Documents Status Changed

```powershell
sqlite3 reims.db "SELECT file_name, status FROM financial_documents WHERE file_name LIKE '%ESP%' LIMIT 5"
# Status should be 'completed' not 'queued'
```

---

## 📊 STEP 4: Update Frontend to Show Real Data

### 4.1 Check Backend API Endpoints

```powershell
# Test KPI endpoint
curl http://localhost:8001/api/kpis/financial

# Test analytics endpoint  
curl http://localhost:8001/api/analytics/dashboard

# Test documents endpoint
curl http://localhost:8001/api/documents
```

### 4.2 If Endpoints Return Empty

We'll need to:
1. Create aggregation service to populate `analytics` table
2. Update KPI endpoint to query from `extracted_data`
3. Create queries to transform extracted data → dashboard KPIs

### 4.3 Refresh Frontend

```powershell
# Frontend should auto-refresh every 30 seconds
# Or manually refresh browser: Ctrl+F5
```

---

## 🔍 Monitoring & Debugging

### Watch Worker Logs
```powershell
# Worker terminal will show:
✅ Job completed: {document_id}
❌ Job failed: {document_id} - {error}
⏳ Processing: {file_name}
```

### Check Queue Status
```python
from queue_service.client import QueueClient
client = QueueClient()

# Check queue length
print(f"Jobs in queue: {client.queue.count}")

# Check failed jobs
failed = client.queue.failed_job_registry
print(f"Failed jobs: {len(failed)}")
```

### Database Queries
```sql
-- Count processed vs queued
SELECT status, COUNT(*) 
FROM financial_documents 
GROUP BY status;

-- View extracted data
SELECT document_id, data_type, extracted_content
FROM extracted_data
LIMIT 5;

-- Check processing jobs
SELECT document_id, status, error_message
FROM processing_jobs
ORDER BY created_at DESC
LIMIT 10;
```

---

## ⚠️ Common Issues & Solutions

### Issue 1: Worker Won't Start
```
Error: Redis connection failed
```
**Solution:**
```powershell
# Check Redis is running
docker ps | findstr redis

# Restart Redis if needed
docker restart reims-redis
```

### Issue 2: Files Not Processing
```
Worker running but no jobs processed
```
**Solution:**
```powershell
# Check if jobs are in Redis queue
redis-cli LLEN rq:queue:document-processing

# Check backend logs
# Files might not be queued properly
```

### Issue 3: Extraction Returns Empty
```
Processed but no data extracted
```
**Solution:**
- Check if PyMuPDF can read the PDF
- Verify PDF format is valid
- Check extraction patterns in `FinancialStatementAgent`

### Issue 4: Frontend Still Shows Hardcoded Data
```
Database has data but frontend doesn't show it
```
**Solution:**
- Backend KPI endpoint needs to query extracted_data
- Need to create aggregation logic
- Frontend components need to use API data instead of hardcoded

---

## 📈 Success Criteria

You'll know it's working when:

✅ Worker terminal shows "Processing document..."  
✅ `financial_documents` status changes from "queued" → "completed"  
✅ `extracted_data` table has records (>1)  
✅ `processing_jobs` status changes to "completed"  
✅ Backend `/api/kpis/financial` returns real data  
✅ Frontend dashboard shows your ESP file data  

---

## 🎯 Quick Start Commands

```powershell
# Terminal 1: Start Worker
.\start_worker.ps1

# Terminal 2: Trigger Processing
curl http://localhost:8001/api/ai-processing/process-all -X POST

# Terminal 3: Monitor Progress
python trace_uploaded_files.py

# After processing: View extracted data
python browse_database.py
```

---

## 📞 Need Help?

If you get stuck at any step:
1. Check worker logs for errors
2. Check backend logs: `backend_error.log`
3. Verify database with: `python browse_database.py`
4. Check Redis: `docker logs reims-redis`

---

**Ready to start? Let's fix this together! 🚀**

**Start with Step 1: Launch the worker in a new terminal**


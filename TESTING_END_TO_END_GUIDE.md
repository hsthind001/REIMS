# REIMS End-to-End Testing Guide

**Complete Step-by-Step Testing Workflow**  
**After uploading files through the frontend**

---

## 📋 **Overview: What to Test**

After uploading a document, you can verify the complete flow through:
1. Frontend upload confirmation
2. MinIO storage verification
3. PostgreSQL database entry
4. Redis queue entry
5. Worker processing
6. AI analysis results
7. Frontend status updates
8. Extracted data viewing

---

## 🧪 **STEP-BY-STEP TESTING GUIDE**

### **Pre-requisites: Uploaded Documents**

You've already uploaded these 3 documents:
1. `ESP 2024 Income Statement.pdf` (ID: `26a710a4-6ac5-4703-90a9-13626ee61685`)
2. `ESP 2024 Cash Flow Statement.pdf` (ID: `2c34fa2c-cf24-4bbb-b9ad-4af92cde13e6`)
3. `ESP 2024 Balance Sheet.pdf` (ID: `59f4550c-5686-4ba9-9df1-51a7c436e4c2`)

---

## **STEP 1: Verify Frontend Upload Success** ✅

### What to Check:
- Document appears in "Recent Uploads" section
- Blue "Queued" badge is visible
- Document info shows (filename, size, upload time)
- Status polling is happening (every 1 second)

### How to Test:
1. **Open Frontend**
   ```
   http://localhost:3001
   ```

2. **Navigate to Upload Tab**
   - Click "Upload" button in navigation

3. **Verify Your Documents**
   - Scroll to "Recent Uploads" section
   - You should see all 3 documents listed
   - Each should have:
     - ✅ Filename visible
     - ✅ Blue badge showing "Queued"
     - ✅ Upload time (just now / minutes ago)
     - ✅ File size
     - ✅ Action buttons (View, Delete)

4. **Check Browser Console (F12)**
   ```javascript
   // Should see polling requests every second
   GET http://localhost:8001/api/documents/{id}/status
   ```

### Expected Result:
✅ All 3 documents visible with "Queued" status

---

## **STEP 2: Verify Document in PostgreSQL Database** 🗄️

### What to Check:
- Document metadata saved
- Correct status (queued)
- Proper timestamps
- File information accurate

### How to Test:

#### Option A: Using psql Command Line
```bash
# Connect to database
psql -h localhost -p 5432 -U postgres -d reims
# Password: dev123

# View all your documents
SELECT 
    id,
    filename,
    status,
    document_type,
    file_size,
    TO_CHAR(upload_date, 'YYYY-MM-DD HH24:MI:SS') as uploaded_at
FROM documents 
WHERE id IN (
    '2c34fa2c-cf24-4bbb-b9ad-4af92cde13e6',
    '59f4550c-5686-4ba9-9df1-51a7c436e4c2'
)
ORDER BY upload_date DESC;
```

#### Option B: Using Python
```python
import psycopg2

conn = psycopg2.connect("postgresql://postgres:dev123@localhost:5432/reims")
cursor = conn.cursor()

cursor.execute("""
    SELECT id, filename, status, upload_date, file_size
    FROM documents 
    ORDER BY upload_date DESC 
    LIMIT 5
""")

for row in cursor.fetchall():
    print(f"ID: {row[0]}")
    print(f"File: {row[1]}")
    print(f"Status: {row[2]}")
    print(f"Uploaded: {row[3]}")
    print(f"Size: {row[4]} bytes")
    print("-" * 50)
```

#### Option C: Using API
```powershell
# Get all documents
curl http://localhost:8001/api/documents | ConvertFrom-Json | ConvertTo-Json -Depth 10

# Get specific document
curl http://localhost:8001/api/documents/2c34fa2c-cf24-4bbb-b9ad-4af92cde13e6 | ConvertFrom-Json
```

### Expected Result:
✅ All documents present in database with status = 'queued'

---

## **STEP 3: Verify File in MinIO Storage** 📦

### What to Check:
- File physically stored in MinIO
- Correct bucket (reims-documents)
- Proper path structure
- File accessible

### How to Test:

#### Option A: MinIO Console (Visual)
```
1. Open MinIO Console: http://localhost:9001
2. Login: minioadmin / minioadmin
3. Navigate to "Buckets" → "reims-documents"
4. Browse to: properties/1/
5. You should see your 3 PDF files with UUID prefixes
```

#### Option B: Using MinIO Client (mc)
```bash
# Configure mc (one-time setup)
mc alias set local http://localhost:9000 minioadmin minioadmin

# List files in bucket
mc ls local/reims-documents/properties/1/

# Expected output:
# [date] [size] 2c34fa2c-cf24-4bbb-b9ad-4af92cde13e6_ESP 2024 Cash Flow Statement.pdf
# [date] [size] 59f4550c-5686-4ba9-9df1-51a7c436e4c2_ESP 2024 Balance Sheet.pdf
```

#### Option C: Using Python (boto3)
```python
from minio import Minio

client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

# List objects in bucket
objects = client.list_objects("reims-documents", prefix="properties/1/", recursive=True)

for obj in objects:
    print(f"File: {obj.object_name}")
    print(f"Size: {obj.size} bytes")
    print(f"Modified: {obj.last_modified}")
    print("-" * 50)
```

#### Option D: Using API
```powershell
# View document (opens in browser)
Start-Process "http://localhost:8001/api/documents/2c34fa2c-cf24-4bbb-b9ad-4af92cde13e6/view"

# Download document
curl http://localhost:8001/api/documents/2c34fa2c-cf24-4bbb-b9ad-4af92cde13e6/download -OutFile downloaded_doc.pdf
```

### Expected Result:
✅ All 3 PDF files stored in MinIO with correct naming

---

## **STEP 4: Verify Job in Redis Queue** ⚡

### What to Check:
- Processing job created
- Job in correct queue (document_processing)
- Job data contains document_id and file_path

### How to Test:

#### Option A: Using redis-cli
```bash
# Connect to Redis
redis-cli -h localhost -p 6379

# Check queue length
LLEN queue:document_processing

# Peek at queue items (without removing)
LRANGE queue:document_processing 0 -1

# Check job details
GET job:{job_id}
```

#### Option B: Using Python
```python
import redis
import json

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Check queue length
queue_length = r.llen('queue:document_processing')
print(f"Jobs in queue: {queue_length}")

# Get all jobs in queue
jobs = r.lrange('queue:document_processing', 0, -1)
for job_data in jobs:
    job = json.loads(job_data)
    print(f"Job ID: {job.get('job_id')}")
    print(f"Document ID: {job.get('job_data', {}).get('document_id')}")
    print(f"Status: {job.get('status')}")
    print("-" * 50)
```

#### Option C: Check via API (if worker endpoint exists)
```powershell
curl http://localhost:8001/api/queue/status
```

### Expected Result:
✅ 3 jobs in document_processing queue (or being processed)

---

## **STEP 5: Verify Worker is Processing** ⚙️

### What to Check:
- Worker service is running
- Worker connected to Redis
- Worker picking up jobs
- Processing logs visible

### How to Test:

#### Check Worker Process
```powershell
# Check if worker is running
Get-Process python | Where-Object { $_.ProcessName -eq "python" }

# Check worker logs (in the terminal where worker is running)
# You should see:
# INFO:__main__:Worker worker_xxx starting to process queues
# INFO:__main__:Processing job {job_id} of type document_processing
```

#### Monitor Worker Activity
```powershell
# In the worker terminal, watch for:
INFO:__main__:Processing job abc123 of type document_processing
INFO:document_processor:Processing document: 2c34fa2c-cf24-4bbb-b9ad-4af92cde13e6
INFO:__main__:Job abc123 completed successfully
```

#### Check Worker Stats (if available)
```python
# If worker exposes stats endpoint
import requests
stats = requests.get('http://localhost:8001/api/worker/stats').json()
print(stats)
```

### Expected Result:
✅ Worker running and processing jobs

---

## **STEP 6: Verify Processing Status Changes** 🔄

### What to Check:
- Status changes from queued → processing → processed
- Processing time recorded
- No errors

### How to Test:

#### Real-time Status Monitoring
```powershell
# PowerShell script to monitor status
$docId = "2c34fa2c-cf24-4bbb-b9ad-4af92cde13e6"

while ($true) {
    $response = curl "http://localhost:8001/api/documents/$docId/status" | ConvertFrom-Json
    $status = $response.data.status
    
    Write-Host "$(Get-Date -Format 'HH:mm:ss') - Status: $status" -ForegroundColor $(
        if ($status -eq "processed") { "Green" }
        elseif ($status -eq "processing") { "Yellow" }
        else { "Cyan" }
    )
    
    if ($status -eq "processed" -or $status -eq "failed") {
        break
    }
    
    Start-Sleep -Seconds 2
}
```

#### Check Database for Status Updates
```sql
-- Check current status
SELECT id, filename, status, upload_date
FROM documents
WHERE id = '2c34fa2c-cf24-4bbb-b9ad-4af92cde13e6';

-- Check if processed_data entry exists
SELECT processing_status, created_at, updated_at
FROM processed_data
WHERE document_id = '2c34fa2c-cf24-4bbb-b9ad-4af92cde13e6';
```

### Expected Result:
✅ Status progresses: queued → processing → processed (takes 5-10 seconds)

---

## **STEP 7: Verify AI Processing Results** 🤖

### What to Check:
- AI analysis completed
- Data extracted and saved
- Insights generated
- Confidence scores calculated

### How to Test:

#### Option A: Check via API
```powershell
# Get document with processing results
$docId = "2c34fa2c-cf24-4bbb-b9ad-4af92cde13e6"
$response = curl "http://localhost:8001/api/documents/$docId" | ConvertFrom-Json

# View the data
$response | ConvertTo-Json -Depth 10
```

#### Option B: Query PostgreSQL
```sql
-- Get AI processing results
SELECT 
    d.filename,
    p.processing_status,
    p.document_type,
    p.confidence_score,
    p.extracted_data::json as extracted_data,
    p.insights::json as insights,
    p.processing_time_seconds
FROM documents d
JOIN processed_data p ON d.id = p.document_id
WHERE d.id = '2c34fa2c-cf24-4bbb-b9ad-4af92cde13e6';
```

#### Option C: View Extracted Data (Formatted)
```sql
-- For Financial Documents - Extract specific metrics
SELECT 
    d.filename,
    p.extracted_data::json->'financial_metrics'->>'revenue' as revenue,
    p.extracted_data::json->'financial_metrics'->>'expenses' as expenses,
    p.extracted_data::json->'financial_metrics'->>'net_income' as net_income,
    p.insights::json->>'summary' as summary,
    p.confidence_score
FROM documents d
JOIN processed_data p ON d.id = p.document_id
WHERE d.document_type = 'financial_statement';
```

#### Option D: Python Script to View Results
```python
import psycopg2
import json

conn = psycopg2.connect("postgresql://postgres:dev123@localhost:5432/reims")
cursor = conn.cursor()

cursor.execute("""
    SELECT 
        d.filename,
        p.extracted_data,
        p.insights,
        p.confidence_score
    FROM documents d
    JOIN processed_data p ON d.id = p.document_id
    WHERE d.id = '2c34fa2c-cf24-4bbb-b9ad-4af92cde13e6'
""")

row = cursor.fetchone()
if row:
    print(f"File: {row[0]}")
    print(f"Confidence: {row[3]}")
    print("\nExtracted Data:")
    print(json.dumps(json.loads(row[1]), indent=2))
    print("\nInsights:")
    print(json.dumps(json.loads(row[2]), indent=2))
```

### Expected Result:
✅ AI extracted financial metrics, document type, and insights

**Example Expected Data (Financial Statement):**
```json
{
  "document_type": "financial_statement",
  "confidence": 0.85,
  "financial_metrics": {
    "revenue": {"primary_value": 250000, "currency": "USD"},
    "expenses": {"primary_value": 180000, "currency": "USD"},
    "net_income": {"primary_value": 70000, "currency": "USD"}
  },
  "insights": {
    "summary": "Financial statement classified with 85% confidence",
    "key_findings": ["Financial data successfully extracted"],
    "recommendations": ["Suitable for automated processing"]
  }
}
```

---

## **STEP 8: Verify Frontend Updates** 💻

### What to Check:
- Frontend polls for status
- Badge color changes (Blue → Yellow → Green)
- Processed badge shows "Processed"
- View/Download buttons work

### How to Test:

#### Visual Verification
```
1. Keep frontend open: http://localhost:3001 → Upload tab
2. Watch the document badge change colors:
   - 🔵 Blue "Queued" (initial)
   - 🟡 Yellow "Processing..." (during processing)
   - 🟢 Green "Processed" (completed)
3. Time it: Should take 5-10 seconds
```

#### Check Browser DevTools
```javascript
// Open DevTools (F12) → Network tab
// Filter: /status
// You'll see requests every 1 second:
GET /api/documents/2c34fa2c-cf24-4bbb-b9ad-4af92cde13e6/status

// Response changes from:
{ "data": { "status": "queued" } }
// to:
{ "data": { "status": "processing" } }
// to:
{ "data": { "status": "processed", "metrics": {...} } }
```

#### Test View Button
```
1. Wait for green "Processed" badge
2. Click "View" button
3. Document should open in new tab
4. URL: http://localhost:8001/api/documents/{id}/view
```

#### Test Download Button
```
1. Click "Download" button
2. File should download to your Downloads folder
3. Open downloaded PDF - should be identical to original
```

### Expected Result:
✅ Frontend updates in real-time, buttons work correctly

---

## **STEP 9: End-to-End Verification** 🎯

### Complete Flow Check
Run this comprehensive test to verify everything:

```powershell
# Complete E2E Test Script
$docId = "2c34fa2c-cf24-4bbb-b9ad-4af92cde13e6"

Write-Host "`n=== REIMS End-to-End Verification ===" -ForegroundColor Cyan
Write-Host "Document ID: $docId`n" -ForegroundColor White

# 1. Check document in database
Write-Host "1. Checking Database..." -ForegroundColor Yellow
$query = "SELECT filename, status FROM documents WHERE id = '$docId'"
# Run query and display

# 2. Check file in MinIO
Write-Host "2. Checking MinIO Storage..." -ForegroundColor Yellow
$viewUrl = "http://localhost:8001/api/documents/$docId/view"
curl -I $viewUrl

# 3. Check processing status
Write-Host "3. Checking Processing Status..." -ForegroundColor Yellow
$status = curl "http://localhost:8001/api/documents/$docId/status" | ConvertFrom-Json
Write-Host "Status: $($status.data.status)" -ForegroundColor Green

# 4. Check processed data (if processed)
if ($status.data.status -eq "processed") {
    Write-Host "4. Checking AI Results..." -ForegroundColor Yellow
    $doc = curl "http://localhost:8001/api/documents/$docId" | ConvertFrom-Json
    Write-Host "Document Type: $($doc.data.document_type)" -ForegroundColor Green
    Write-Host "Confidence: $($doc.data.confidence_score)" -ForegroundColor Green
}

Write-Host "`n=== Verification Complete ===" -ForegroundColor Green
```

---

## **STEP 10: Test All 3 Documents** 📊

### Batch Testing Script
```powershell
# Test all your uploaded documents
$documents = @(
    "2c34fa2c-cf24-4bbb-b9ad-4af92cde13e6",
    "59f4550c-5686-4ba9-9df1-51a7c436e4c2"
)

foreach ($docId in $documents) {
    Write-Host "`n--- Testing Document: $docId ---" -ForegroundColor Cyan
    
    $response = curl "http://localhost:8001/api/documents/$docId/status" | ConvertFrom-Json
    
    Write-Host "Filename: $($response.data.filename)" -ForegroundColor White
    Write-Host "Status: $($response.data.status)" -ForegroundColor $(
        if ($response.data.status -eq "processed") { "Green" }
        elseif ($response.data.status -eq "processing") { "Yellow" }
        else { "Cyan" }
    )
    
    if ($response.data.metrics) {
        Write-Host "Metrics Found: $($response.data.metrics | ConvertTo-Json -Compress)" -ForegroundColor Gray
    }
}
```

---

## **TROUBLESHOOTING** 🔧

### Issue: Documents Stuck in "Queued"

**Diagnosis:**
```powershell
# Check if worker is running
Get-Process python
# Should show worker process

# Check worker logs
# Look for errors in worker terminal
```

**Solution:**
```powershell
# Restart worker
cd C:\REIMS\queue_service
python worker.py
```

---

### Issue: Status Not Updating in Frontend

**Diagnosis:**
```javascript
// Check browser console (F12)
// Look for polling requests every 1 second
// Check for errors
```

**Solution:**
```
1. Refresh browser (Ctrl+R)
2. Clear cache (Ctrl+Shift+Delete)
3. Check backend is running on port 8001
```

---

### Issue: No Data in processed_data Table

**Diagnosis:**
```sql
-- Check if document exists
SELECT * FROM documents WHERE id = 'your-document-id';

-- Check worker logs for errors
```

**Solution:**
- Check worker is running
- Check Ollama is running (port 11434)
- Check worker logs for errors

---

## **VERIFICATION CHECKLIST** ✅

Complete this checklist for each uploaded document:

- [ ] Document appears in frontend "Recent Uploads"
- [ ] Document exists in PostgreSQL `documents` table
- [ ] File exists in MinIO storage (check console)
- [ ] Job created in Redis queue
- [ ] Worker picks up and processes job
- [ ] Status changes: queued → processing → processed
- [ ] Entry created in `processed_data` table
- [ ] AI extracted data is present
- [ ] Frontend badge turns green
- [ ] View button opens document
- [ ] Download button downloads file
- [ ] Extracted data visible via API

---

## **QUICK TEST COMMANDS**

### One-Line Status Check
```powershell
curl "http://localhost:8001/api/documents/2c34fa2c-cf24-4bbb-b9ad-4af92cde13e6/status" | ConvertFrom-Json
```

### One-Line Database Check
```bash
psql -h localhost -p 5432 -U postgres -d reims -c "SELECT filename, status FROM documents ORDER BY upload_date DESC LIMIT 5;"
```

### One-Line MinIO Check
```bash
mc ls local/reims-documents/properties/1/
```

### One-Line Worker Check
```powershell
Get-Process python | Select-Object Id,ProcessName,StartTime
```

---

## **EXPECTED TIMELINE**

| Step | Time | What Happens |
|------|------|--------------|
| Upload | 0s | File sent to backend |
| Save to MinIO | 1-2s | File stored in object storage |
| Database Entry | <1s | Metadata saved |
| Queue Job | <1s | Job added to Redis |
| Worker Pickup | 1-5s | Worker dequeues job |
| Processing | 2-3s | Extract text, analyze |
| AI Analysis | 2-5s | Ollama processes document |
| Save Results | <1s | Write to processed_data |
| Frontend Update | 1s | Next polling cycle |
| **Total** | **5-10s** | **End-to-end complete** |

---

## **SUCCESS CRITERIA** 🎉

Your end-to-end test is successful when:

1. ✅ All 3 documents show "Processed" status in frontend
2. ✅ All documents have entries in both `documents` and `processed_data` tables
3. ✅ All files are viewable via View button
4. ✅ All files are downloadable
5. ✅ AI extracted meaningful data (revenue, expenses, etc.)
6. ✅ Confidence scores > 0.7
7. ✅ No errors in worker logs
8. ✅ Processing time < 15 seconds per document

---

**You're testing a complete, production-ready document processing pipeline!** 🚀















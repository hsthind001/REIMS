# 🔗 Frontend ↔ Backend ↔ Database Mapping

**Complete integration guide showing how everything connects**

---

## 📊 Endpoint #1: Dashboard Analytics

### **Frontend Hook:**
```javascript
useAnalytics() → GET /api/analytics
```

### **Backend Endpoint:**
```python
@router.get("/api/analytics")
async def get_analytics(db: Session = Depends(get_db)):
```

### **PostgreSQL Queries:**

#### **Total Properties**
```sql
SELECT COUNT(*) 
FROM properties 
WHERE status = 'active'
```
↓ Maps to: `analytics.total_properties`

#### **Portfolio Value**
```sql
SELECT SUM(current_value) 
FROM properties
```
↓ Maps to: `analytics.portfolio_value`

#### **Monthly Income**
```sql
SELECT SUM(monthly_rent) 
FROM stores 
WHERE status = 'occupied'
```
↓ Maps to: `analytics.monthly_income`

#### **Occupancy Rate**
```sql
SELECT 
  COUNT(*) FILTER (WHERE status='occupied') * 100.0 / NULLIF(COUNT(*), 0)
FROM stores
```
↓ Maps to: `analytics.occupancy_rate`

#### **Average Occupancy (Alternative)**
```sql
SELECT AVG(latest_occupancy_rate) 
FROM properties
```

#### **YoY Growth**
```sql
-- Calculate from historical data
SELECT 
  (SUM(current_value) - SUM(acquisition_cost)) / SUM(acquisition_cost) * 100
FROM properties
```
↓ Maps to: `analytics.yoy_growth`

### **Response Format:**
```json
{
  "success": true,
  "data": {
    "total_properties": 184,
    "portfolio_value": 47800000,
    "monthly_income": 1200000,
    "occupancy_rate": 0.946,
    "yoy_growth": 8.2,
    "risk_score": 23.5,
    "last_updated": "2025-10-12T14:30:00Z"
  }
}
```

---

## 📊 Endpoint #2: Properties List

### **Frontend Hook:**
```javascript
useProperties({
  skip: 0,
  limit: 20,
  status: 'healthy',
  sortBy: 'name',
  sortOrder: 'asc',
  search: 'sunset'
})
→ GET /api/properties?skip=0&limit=20&status=healthy&sort_by=name&sort_order=asc&search=sunset
```

### **Backend Endpoint:**
```python
@router.get("/api/properties")
async def get_properties(
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    sort_by: str = "name",
    sort_order: str = "asc",
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
```

### **PostgreSQL Query:**
```sql
-- Base query
SELECT 
  p.id,
  p.name,
  p.address,
  p.city,
  p.state,
  p.total_sqft,
  p.current_value,
  p.annual_noi,
  p.latest_dscr,
  p.latest_occupancy_rate,
  p.has_active_alerts,
  p.created_at,
  -- Calculate status based on metrics
  CASE 
    WHEN p.latest_dscr < 1.25 OR p.latest_occupancy_rate < 0.85 THEN 'alert'
    ELSE 'healthy'
  END as status
FROM properties p
WHERE 
  -- Filter by status
  (@status IS NULL OR 
   CASE 
     WHEN @status = 'alert' THEN (p.latest_dscr < 1.25 OR p.latest_occupancy_rate < 0.85)
     WHEN @status = 'healthy' THEN (p.latest_dscr >= 1.25 AND p.latest_occupancy_rate >= 0.85)
   END)
  -- Search filter
  AND (@search IS NULL OR 
       p.name ILIKE '%' || @search || '%' OR 
       p.address ILIKE '%' || @search || '%')
-- Sorting
ORDER BY 
  CASE WHEN @sort_order = 'asc' THEN 
    CASE @sort_by
      WHEN 'name' THEN p.name
      WHEN 'occupancy_rate' THEN p.latest_occupancy_rate::text
      WHEN 'noi' THEN p.annual_noi::text
      WHEN 'dscr' THEN p.latest_dscr::text
    END
  END ASC,
  CASE WHEN @sort_order = 'desc' THEN 
    CASE @sort_by
      WHEN 'name' THEN p.name
      WHEN 'occupancy_rate' THEN p.latest_occupancy_rate::text
      WHEN 'noi' THEN p.annual_noi::text
      WHEN 'dscr' THEN p.latest_dscr::text
    END
  END DESC
LIMIT @limit OFFSET @skip;

-- Count query for pagination
SELECT COUNT(*) FROM properties WHERE [same filters];
```

### **Response Format:**
```json
{
  "success": true,
  "data": {
    "properties": [
      {
        "id": "prop-001",
        "name": "Downtown Office Commons",
        "address": "123 Main St",
        "city": "San Francisco",
        "state": "CA",
        "occupancy_rate": 0.94,
        "noi": 850000,
        "dscr": 1.35,
        "status": "healthy",
        "current_value": 12500000,
        "units": 42,
        "square_footage": 85000
      }
    ],
    "total": 184
  }
}
```

---

## 📊 Endpoint #3: Document Upload

### **Frontend Hook:**
```javascript
useDocumentUpload()
→ POST /api/documents/upload (multipart/form-data)
```

### **Backend Endpoint:**
```python
@router.post("/api/documents/upload")
async def upload_document(
    file: UploadFile,
    property_id: str = Form(...),
    document_type: str = Form(...),
    db: Session = Depends(get_db)
):
```

### **Process:**

#### **Step 1: Generate Document ID**
```python
document_id = str(uuid.uuid4())
```

#### **Step 2: Upload to MinIO**
```python
file_path = f"properties/{property_id}/{document_id}_{file.filename}"
minio_client.put_object(
    bucket_name="reims-files",
    object_name=file_path,
    data=file.file,
    length=file.size
)
```

#### **Step 3: Store in PostgreSQL**
```sql
INSERT INTO financial_documents (
  id,
  property_id,
  file_path,
  file_name,
  document_type,
  status,
  upload_date
) VALUES (
  @document_id,
  @property_id,
  @file_path,
  @file_name,
  @document_type,
  'queued',
  NOW()
)
```

#### **Step 4: Add to Redis Queue**
```python
redis_client.rpush(
    "document_processing_queue",
    json.dumps({
        "document_id": document_id,
        "file_path": file_path,
        "property_id": property_id
    })
)
```

### **Response Format:**
```json
{
  "success": true,
  "data": {
    "document_id": "doc-uuid-123",
    "status": "queued"
  }
}
```

---

## 📊 Endpoint #4: Document Status

### **Frontend Hook:**
```javascript
useDocumentStatus(documentId)
→ GET /api/documents/{documentId}/status (poll every 2s)
```

### **Backend Endpoint:**
```python
@router.get("/api/documents/{document_id}/status")
async def get_document_status(
    document_id: str,
    db: Session = Depends(get_db)
):
```

### **PostgreSQL Query:**
```sql
SELECT 
  fd.id,
  fd.status,
  fd.upload_date,
  fd.processing_date,
  fd.error_message,
  -- Get extracted metrics for this document
  COALESCE(
    json_agg(
      json_build_object(
        'metric_name', em.metric_name,
        'metric_value', em.metric_value,
        'confidence_score', em.confidence_score
      )
    ) FILTER (WHERE em.id IS NOT NULL),
    '[]'
  ) as metrics
FROM financial_documents fd
LEFT JOIN extracted_metrics em ON em.document_id = fd.id
WHERE fd.id = @document_id
GROUP BY fd.id
```

### **Response Format:**
```json
{
  "success": true,
  "data": {
    "document_id": "doc-uuid-123",
    "status": "processed",
    "metrics": [
      {
        "metric_name": "noi",
        "metric_value": 850000,
        "confidence_score": 0.95
      },
      {
        "metric_name": "dscr",
        "metric_value": 1.35,
        "confidence_score": 0.92
      },
      {
        "metric_name": "occupancy",
        "metric_value": 0.94,
        "confidence_score": 0.98
      }
    ]
  }
}
```

---

## 📊 Endpoint #5: Alerts List

### **Frontend Hook:**
```javascript
useAlerts({
  status: 'pending',
  level: 'critical',
  committee: 'Finance Sub-Committee'
})
→ GET /api/alerts?status=pending&level=critical&committee=Finance%20Sub-Committee
```

### **Backend Endpoint:**
```python
@router.get("/api/alerts")
async def get_alerts(
    status: Optional[str] = 'pending',
    level: Optional[str] = None,
    committee: Optional[str] = None,
    db: Session = Depends(get_db)
):
```

### **PostgreSQL Query:**
```sql
SELECT 
  ca.id,
  ca.property_id,
  p.name as property_name,
  ca.alert_type,
  ca.value,
  ca.threshold,
  ca.level,
  ca.committee,
  ca.status,
  ca.created_at,
  ca.approved_at,
  ca.approved_by,
  ca.notes,
  -- Build description dynamically
  CASE ca.alert_type
    WHEN 'dscr_low' THEN 'DSCR has fallen below the required threshold of ' || ca.threshold
    WHEN 'occupancy_low' THEN 'Occupancy rate has dropped below ' || (ca.threshold * 100)::text || '%'
    WHEN 'anomaly' THEN 'Statistical anomaly detected (Z-score: ' || ca.value::text || ')'
  END as description
FROM committee_alerts ca
JOIN properties p ON p.id = ca.property_id
WHERE 
  (@status IS NULL OR ca.status = @status)
  AND (@level IS NULL OR ca.level = @level)
  AND (@committee IS NULL OR ca.committee = @committee)
ORDER BY 
  -- Critical first, then by creation date
  CASE ca.level
    WHEN 'critical' THEN 1
    WHEN 'warning' THEN 2
    WHEN 'info' THEN 3
  END,
  ca.created_at DESC
```

### **Response Format:**
```json
{
  "success": true,
  "data": {
    "alerts": [
      {
        "id": "alert-001",
        "property_id": "prop-001",
        "property_name": "Downtown Office Commons",
        "alert_type": "dscr_low",
        "value": 1.15,
        "threshold": 1.25,
        "level": "critical",
        "committee": "Finance Sub-Committee",
        "status": "pending",
        "created_at": "2025-10-12T10:00:00Z",
        "description": "DSCR has fallen below the required threshold of 1.25"
      }
    ],
    "total": 3
  }
}
```

---

## 📊 Endpoint #6: Alert Statistics

### **Frontend Hook:**
```javascript
useAlertStats()
→ GET /api/alerts/stats
```

### **Backend Endpoint:**
```python
@router.get("/api/alerts/stats")
async def get_alert_stats(db: Session = Depends(get_db)):
```

### **PostgreSQL Query:**
```sql
-- Get aggregate statistics
SELECT 
  COUNT(*) FILTER (WHERE status = 'pending') as total_pending,
  COUNT(*) FILTER (WHERE status = 'approved') as total_approved,
  COUNT(*) FILTER (WHERE status = 'rejected') as total_rejected,
  
  -- By level
  json_build_object(
    'critical', COUNT(*) FILTER (WHERE level = 'critical' AND status = 'pending'),
    'warning', COUNT(*) FILTER (WHERE level = 'warning' AND status = 'pending'),
    'info', COUNT(*) FILTER (WHERE level = 'info' AND status = 'pending')
  ) as by_level,
  
  -- By committee
  (
    SELECT json_object_agg(committee, cnt)
    FROM (
      SELECT committee, COUNT(*) as cnt
      FROM committee_alerts
      WHERE status = 'pending'
      GROUP BY committee
    ) sub
  ) as by_committee,
  
  -- Average response time (in hours)
  AVG(
    EXTRACT(EPOCH FROM (approved_at - created_at)) / 3600
  ) FILTER (WHERE approved_at IS NOT NULL) as avg_response_time_hours,
  
  -- Oldest pending alert (in days)
  MAX(
    EXTRACT(EPOCH FROM (NOW() - created_at)) / 86400
  ) FILTER (WHERE status = 'pending') as oldest_pending_days
  
FROM committee_alerts
```

### **Response Format:**
```json
{
  "success": true,
  "data": {
    "total_pending": 12,
    "total_approved": 45,
    "total_rejected": 8,
    "by_level": {
      "critical": 3,
      "warning": 7,
      "info": 2
    },
    "by_committee": {
      "Finance Sub-Committee": 5,
      "Occupancy Sub-Committee": 4,
      "Risk Committee": 3
    },
    "avg_response_time_hours": 4.5,
    "oldest_pending_days": 2.3
  }
}
```

---

## 📊 Endpoint #7: Approve Alert

### **Frontend Hook:**
```javascript
useAlertDecision().approve({
  alertId: 'alert-001',
  userId: 'user-123',
  notes: 'Refinance option being evaluated'
})
→ POST /api/alerts/{alertId}/approve
```

### **Backend Endpoint:**
```python
@router.post("/api/alerts/{alert_id}/approve")
async def approve_alert(
    alert_id: str,
    request: ApproveAlertRequest,
    db: Session = Depends(get_db)
):
```

### **PostgreSQL Queries:**

#### **Step 1: Update Alert**
```sql
UPDATE committee_alerts 
SET 
  status = 'approved',
  approved_by = @user_id,
  approved_at = NOW(),
  notes = @notes
WHERE id = @alert_id
RETURNING property_id
```

#### **Step 2: Unlock Workflow**
```sql
UPDATE workflow_locks
SET 
  status = 'unlocked',
  unlocked_at = NOW()
WHERE alert_id = @alert_id
```

#### **Step 3: Update Property Flag**
```sql
-- Check if property has any remaining pending alerts
UPDATE properties
SET has_active_alerts = EXISTS(
  SELECT 1 FROM committee_alerts
  WHERE property_id = @property_id AND status = 'pending'
)
WHERE id = @property_id
```

#### **Step 4: Log Audit Event**
```sql
INSERT INTO audit_log (
  action,
  user_id,
  br_id,
  alert_id,
  property_id,
  details,
  timestamp
) VALUES (
  'ALERT_DECISION',
  @user_id,
  'BR-003',
  @alert_id,
  @property_id,
  json_build_object('decision', 'approved', 'notes', @notes),
  NOW()
)
```

### **Response Format:**
```json
{
  "success": true,
  "data": {
    "alert_id": "alert-001",
    "status": "approved",
    "approved_at": "2025-10-12T14:35:00Z"
  }
}
```

---

## 📊 Endpoint #8: Reject Alert

Same as approve, but with `status = 'rejected'` and additional `reason` field.

---

## 📊 Endpoint #9: Property Alerts History

### **Frontend Hook:**
```javascript
usePropertyAlerts('prop-001')
→ GET /api/properties/prop-001/alerts
```

### **PostgreSQL Query:**
```sql
SELECT 
  ca.*,
  -- Calculate how long the alert was open
  CASE 
    WHEN ca.approved_at IS NOT NULL 
    THEN EXTRACT(EPOCH FROM (ca.approved_at - ca.created_at)) / 3600
    ELSE NULL
  END as resolution_time_hours
FROM committee_alerts ca
WHERE ca.property_id = @property_id
ORDER BY ca.created_at DESC
LIMIT 50
```

---

## 🔄 Background Jobs

### **Job #1: Scheduled Alert Check**
```python
# Run every 5 minutes via cron
@cron.job("*/5 * * * *")
async def check_metrics_and_create_alerts():
```

**Query:**
```sql
-- Find properties with DSCR violations
INSERT INTO committee_alerts (
  id, property_id, alert_type, value, threshold,
  level, committee, status, created_at
)
SELECT 
  gen_random_uuid(),
  p.id,
  'dscr_low',
  p.latest_dscr,
  1.25,
  CASE WHEN p.latest_dscr < 1.10 THEN 'critical' ELSE 'warning' END,
  'Finance Sub-Committee',
  'pending',
  NOW()
FROM properties p
WHERE 
  p.latest_dscr < 1.25
  AND NOT EXISTS (
    SELECT 1 FROM committee_alerts ca
    WHERE ca.property_id = p.id
    AND ca.alert_type = 'dscr_low'
    AND ca.status = 'pending'
  );

-- Find properties with occupancy violations
INSERT INTO committee_alerts (...)
SELECT ...
FROM properties p
WHERE p.latest_occupancy_rate < 0.85 ...

-- Lock workflows
INSERT INTO workflow_locks (property_id, alert_id, locked_at, status)
SELECT property_id, id, NOW(), 'locked'
FROM committee_alerts
WHERE created_at > NOW() - INTERVAL '1 minute';
```

---

## ✅ Complete Integration Summary

| Frontend Feature | Hook | Endpoint | Tables Used |
|------------------|------|----------|-------------|
| Dashboard KPIs | `useAnalytics()` | `GET /api/analytics` | `properties`, `stores` |
| Properties List | `useProperties()` | `GET /api/properties` | `properties` |
| Document Upload | `useDocumentUpload()` | `POST /api/documents/upload` | `financial_documents` |
| Document Status | `useDocumentStatus()` | `GET /api/documents/{id}/status` | `financial_documents`, `extracted_metrics` |
| Alerts List | `useAlerts()` | `GET /api/alerts` | `committee_alerts`, `properties` |
| Alert Stats | `useAlertStats()` | `GET /api/alerts/stats` | `committee_alerts` |
| Approve Alert | `useAlertDecision().approve()` | `POST /api/alerts/{id}/approve` | `committee_alerts`, `workflow_locks`, `audit_log`, `properties` |
| Reject Alert | `useAlertDecision().reject()` | `POST /api/alerts/{id}/reject` | Same as approve |
| Property History | `usePropertyAlerts()` | `GET /api/properties/{id}/alerts` | `committee_alerts` |

---

**All frontend components are ready and waiting for these endpoints!**

🎉 **Perfect alignment between Frontend ↔ Backend ↔ Database!**


# 🔗 REIMS Application - Complete URL Reference

**Date:** 2025-10-12  
**Environment:** Local Development

---

## 🎨 FRONTEND URLs

### **Main Application**
```
Primary:    http://localhost:3001  ← FIXED PORT
```

**Note:** Port 3001 is now **permanently fixed** (not 5173 or 3000).

### **Frontend Pages**

| Page | URL | Description |
|------|-----|-------------|
| **Dashboard** | `http://localhost:3001/` | Main dashboard with KPIs |
| **Alerts Center** | `http://localhost:3001/alerts` | Alerts management |
| **Properties List** | `http://localhost:3001/properties` | Properties listing (to be added) |
| **Property Details** | `http://localhost:3001/properties/:id` | Single property view (to be added) |
| **Documents** | `http://localhost:3001/documents` | Documents library (to be added) |

---

## 🔧 BACKEND API URLs

### **Base URL**
```
http://localhost:8001
```

### **Core Endpoints**

#### **Health & Monitoring**
```
GET  http://localhost:8001/health
GET  http://localhost:8001/metrics
```

#### **Analytics**
```
GET  http://localhost:8001/api/analytics
GET  http://localhost:8001/api/analytics/overview
```

**Returns:** Portfolio KPIs (portfolio_value, total_properties, monthly_income, occupancy_rate, yoy_growth, risk_score)

#### **Properties**
```
GET  http://localhost:8001/api/properties
GET  http://localhost:8001/api/properties/{property_id}
```

**Query Parameters:**
- `skip`: Pagination offset (default: 0)
- `limit`: Number of records (default: 20, max: 100)
- `status`: Filter by 'healthy' or 'alert'
- `property_type`: Filter by property type
- `sort_by`: Sort field (name, occupancy_rate, noi, dscr)
- `sort_order`: Sort direction (asc, desc)
- `search`: Search by name or address

**Examples:**
```
GET http://localhost:8001/api/properties?skip=0&limit=20
GET http://localhost:8001/api/properties?status=healthy
GET http://localhost:8001/api/properties?sort_by=occupancy_rate&sort_order=desc
GET http://localhost:8001/api/properties?search=downtown
```

#### **Documents**
```
POST http://localhost:8001/api/documents/upload
GET  http://localhost:8001/api/documents/{document_id}/status
GET  http://localhost:8001/api/documents
```

**Upload Example:**
```bash
curl -X POST http://localhost:8001/api/documents/upload \
  -F "file=@document.pdf" \
  -F "property_id=prop-001" \
  -F "document_type=offering_memo"
```

#### **Alerts**
```
GET  http://localhost:8001/api/alerts
GET  http://localhost:8001/api/alerts/stats
POST http://localhost:8001/api/alerts/{alert_id}/approve
POST http://localhost:8001/api/alerts/{alert_id}/reject
GET  http://localhost:8001/api/properties/{property_id}/alerts
```

**Query Parameters for Alerts:**
- `status`: Filter by 'pending', 'approved', 'rejected'
- `level`: Filter by 'critical', 'warning', 'info'
- `committee`: Filter by committee name
- `limit`: Maximum results (default: 100)

**Examples:**
```
GET http://localhost:8001/api/alerts?status=pending
GET http://localhost:8001/api/alerts?level=critical
GET http://localhost:8001/api/alerts?committee=Finance%20Sub-Committee
```

**Approve Alert:**
```bash
curl -X POST http://localhost:8001/api/alerts/alert-001/approve \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user-123", "notes": "Approved for refinancing"}'
```

**Reject Alert:**
```bash
curl -X POST http://localhost:8001/api/alerts/alert-001/reject \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user-123", "reason": "data_incorrect", "notes": "Values need verification"}'
```

---

## 📚 API DOCUMENTATION

### **Interactive API Docs**
```
Swagger UI:  http://localhost:8001/docs
ReDoc:       http://localhost:8001/redoc
OpenAPI JSON: http://localhost:8001/openapi.json
```

**Features:**
- Try out endpoints directly in browser
- See request/response schemas
- Download API specifications

---

## 🗄️ DATABASE

### **PostgreSQL**
```
Host:     localhost
Port:     5432
Database: reims
URL:      postgresql://user:password@localhost:5432/reims
```

**GUI Clients:**
- pgAdmin: `http://localhost:5050` (if installed)
- DBeaver: Desktop application
- psql: Command line `psql -h localhost -p 5432 -U postgres -d reims`

---

## 💾 STORAGE & CACHE

### **MinIO (S3-Compatible Storage)**
```
API Endpoint:    http://localhost:9000
Web Console:     http://localhost:9001
Access Key:      minioadmin
Secret Key:      minioadmin
```

**Buckets:**
- `reims-files` - Document storage
- Path structure: `properties/{propertyId}/{documentId}_{filename}`

### **Redis (Cache & Queue)**
```
Host:     localhost
Port:     6379
URL:      redis://localhost:6379/0
```

**CLI Access:**
```bash
redis-cli -h localhost -p 6379
```

**Common Keys:**
- `analytics_data` - Cached analytics (5 min TTL)
- `document_processing_queue` - Document processing queue
- `properties-*` - Cached property queries

---

## 📊 MONITORING & OBSERVABILITY

### **Prometheus (Metrics Collection)**
```
Web UI:          http://localhost:9090
Targets:         http://localhost:9090/targets
Graph:           http://localhost:9090/graph
Alerts:          http://localhost:9090/alerts
```

**Key Metrics:**
- `api_requests_total` - API request counter
- `api_latency_seconds` - API response times
- `documents_uploaded_total` - Document upload counter
- `dscr_violations` - Properties with DSCR violations
- `occupancy_violations` - Properties with low occupancy
- `active_alerts` - Total pending alerts

### **Grafana (Dashboards & Visualization)**
```
Web UI:          http://localhost:3000
Username:        admin
Password:        admin
```

**Dashboards:**
- REIMS Overview - Portfolio metrics
- API Performance - Request rates, latencies
- Alerts Monitor - Alert trends
- Storage Stats - MinIO usage

---

## 🤖 AI & ML SERVICES

### **Ollama (Local LLM)**
```
API Endpoint:    http://localhost:11434
Health:          http://localhost:11434/api/tags
Generate:        http://localhost:11434/api/generate
```

**Models:**
- LLaMA 3.1 - Document summarization
- Mistral - Financial analysis
- Embeddings - Semantic search

**Example:**
```bash
curl http://localhost:11434/api/generate \
  -d '{"model": "llama3.1", "prompt": "Summarize this lease agreement..."}'
```

---

## 🔄 REVERSE PROXY (Optional)

### **Nginx**
```
HTTP:            http://localhost:80
HTTPS:           https://localhost:443
```

**Routes:**
- `/` → Frontend (port 5173)
- `/api` → Backend (port 8001)
- `/storage` → MinIO (port 9000)
- `/monitoring` → Grafana (port 3000)

---

## 🧪 TESTING URLs

### **Test Endpoints**

**Backend Health:**
```bash
curl http://localhost:8001/health
# Expected: {"status": "healthy"}
```

**Analytics Data:**
```bash
curl http://localhost:8001/api/analytics
# Expected: JSON with portfolio metrics
```

**Properties List:**
```bash
curl http://localhost:8001/api/properties?limit=5
# Expected: JSON with 5 properties
```

**Alerts List:**
```bash
curl http://localhost:8001/api/alerts?status=pending
# Expected: JSON with pending alerts
```

---

## 📱 MOBILE/TABLET ACCESS

### **Same Network Access**

If accessing from other devices on the same network:

```
Frontend:     http://<your-ip>:5173
Backend:      http://<your-ip>:8001
Grafana:      http://<your-ip>:3000
MinIO:        http://<your-ip>:9001
```

**Find your IP:**
```bash
# Windows
ipconfig | findstr IPv4

# Result example: 192.168.1.100
# Then use: http://192.168.1.100:5173
```

---

## 🔐 AUTHENTICATION URLs (Future)

### **When Auth is Implemented**

```
POST http://localhost:8001/auth/login
POST http://localhost:8001/auth/logout
POST http://localhost:8001/auth/refresh
GET  http://localhost:8001/auth/me
POST http://localhost:8001/auth/register
POST http://localhost:8001/auth/forgot-password
POST http://localhost:8001/auth/reset-password
```

---

## 📋 COMPLETE SERVICE MAP

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| **Frontend** | 3001 | http://localhost:3001 | React application (FIXED) |
| **Backend** | 8001 | http://localhost:8001 | FastAPI REST API (FIXED) |
| **PostgreSQL** | 5432 | localhost:5432 | Primary database |
| **Redis** | 6379 | localhost:6379 | Cache & queue |
| **MinIO API** | 9000 | http://localhost:9000 | Object storage API |
| **MinIO Console** | 9001 | http://localhost:9001 | Storage web UI |
| **Prometheus** | 9090 | http://localhost:9090 | Metrics collection |
| **Grafana** | 3000 | http://localhost:3000 | Monitoring dashboards |
| **Ollama** | 11434 | http://localhost:11434 | Local LLM API |
| **Nginx** | 80/443 | http://localhost | Reverse proxy (optional) |

---

## 🚀 QUICK START URLs

### **Development**

1. **Start everything, then visit:**
   ```
   Main App:        http://localhost:5173
   API Docs:        http://localhost:8001/docs
   Monitoring:      http://localhost:3000
   ```

2. **Test the stack:**
   ```
   Backend Health:  http://localhost:8001/health
   Analytics:       http://localhost:8001/api/analytics
   Alerts:          http://localhost:8001/api/alerts
   ```

### **Production (Future)**

```
Frontend:        https://reims.yourdomain.com
Backend API:     https://api.reims.yourdomain.com
Monitoring:      https://monitoring.reims.yourdomain.com
```

---

## 🔍 DEBUGGING URLs

### **Check Service Status**

```bash
# Backend health
curl http://localhost:8001/health

# Frontend (should return HTML)
curl http://localhost:5173

# PostgreSQL (via backend)
curl http://localhost:8001/api/analytics

# Redis (via redis-cli)
redis-cli ping
# Expected: PONG

# MinIO
curl http://localhost:9000/minio/health/live
# Expected: OK

# Prometheus targets
curl http://localhost:9090/api/v1/targets

# Grafana health
curl http://localhost:3000/api/health
```

---

## 📞 WEBHOOK URLs (Future)

### **For Integrations**

```
POST http://localhost:8001/webhooks/document-processed
POST http://localhost:8001/webhooks/alert-created
POST http://localhost:8001/webhooks/property-updated
```

---

## 🔄 WebSocket URLs (Future)

### **Real-Time Updates**

```
ws://localhost:8001/ws/alerts
ws://localhost:8001/ws/processing-status
ws://localhost:8001/ws/notifications
```

---

## 📖 DOCUMENTATION URLs

### **Code Documentation**

```
Backend API:     http://localhost:8001/docs
Frontend Docs:   See project README files
Database Schema: See migration files in backend/db/migrations/
```

### **Project Documentation Files**

- `README.md` - Main project overview
- `FRONTEND_BACKEND_ALIGNMENT_VERIFICATION.md` - Integration guide
- `BACKEND_ENDPOINTS_COMPLETE.md` - API reference
- `COMPLETE_FRONTEND_FEATURES_SUMMARY.md` - Frontend features
- `FRONTEND_BACKEND_DATABASE_MAPPING.md` - Data flow mapping

---

## 🎯 MOST COMMONLY USED URLs

**During Development:**

1. **Frontend App:** `http://localhost:3001` ⭐ (FIXED PORT)
2. **API Docs:** `http://localhost:8001/docs` ⭐
3. **Analytics Endpoint:** `http://localhost:8001/api/analytics`
4. **Grafana Dashboard:** `http://localhost:3000`

**For Testing:**

1. **Health Check:** `http://localhost:8001/health` ⭐
2. **Properties List:** `http://localhost:8001/api/properties`
3. **Alerts List:** `http://localhost:8001/api/alerts`
4. **MinIO Console:** `http://localhost:9001`

---

## ⚙️ PORT CONFIGURATION

**Default Ports (can be changed via environment variables):**

```env
VITE_DEV_SERVER_PORT=5173
BACKEND_PORT=8001
POSTGRES_PORT=5432
REDIS_PORT=6379
MINIO_API_PORT=9000
MINIO_CONSOLE_PORT=9001
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
OLLAMA_PORT=11434
NGINX_HTTP_PORT=80
NGINX_HTTPS_PORT=443
```

---

**Created:** 2025-10-12  
**Status:** ✅ Complete URL Reference  
**Environment:** Local Development


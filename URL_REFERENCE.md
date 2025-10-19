# REIMS System URLs & API Reference

## 🌐 System Overview

### Core Services
- **Backend API Server**: http://localhost:8000
- **Frontend Application**: http://localhost:5175
- **Storage Service (MinIO)**: http://localhost:9000
- **MinIO Admin Console**: http://localhost:9001

### Documentation & Health
- **API Documentation (Swagger)**: http://localhost:8000/docs
- **API Documentation (ReDoc)**: http://localhost:8000/redoc
- **System Health Check**: http://localhost:8000/health

## 📋 Complete API Endpoint Reference

### 🔧 System Health & Status

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Main system health check |
| GET | `/analytics/health` | AI processing service health |
| GET | `/queue/health` | Queue management service health |
| GET | `/storage/health` | Storage service health |

### 📄 Document Management

#### Upload & Processing
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/documents/upload` | Upload new document |
| GET | `/api/documents/{document_id}` | Get specific document details |
| GET | `/api/documents` | List all documents |
| GET | `/api/documents/{document_id}/processed` | Get processed document data |

#### Storage Operations
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload` | Alternative upload endpoint |
| GET | `/documents/{document_id}` | Retrieve document from storage |
| GET | `/documents` | List stored documents |
| DELETE | `/documents/{document_id}` | Delete document |
| GET | `/statistics` | Storage statistics |
| POST | `/backup/{document_id}` | Backup specific document |
| POST | `/archive` | Archive documents |

### 🤖 AI Processing

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/process/{document_id}` | Process specific document |
| GET | `/process/{document_id}/status` | Check processing status |
| GET | `/processed-data/{document_id}` | Get processed data |
| POST | `/process-all` | Process all pending documents |
| GET | `/analytics/processing-stats` | Processing statistics |
| GET | `/analytics/extraction-summary` | Data extraction summary |

### 🏢 Property Management

#### Properties
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/properties` | Create new property |
| GET | `/properties` | List all properties |
| GET | `/properties/{property_id}` | Get specific property |
| PUT | `/properties/{property_id}` | Update property |

#### Tenants
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tenants` | Create new tenant |
| GET | `/tenants` | List all tenants |

#### Leases
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/leases` | Create new lease |
| GET | `/leases` | List all leases |

#### Maintenance
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/maintenance` | Create maintenance request |
| GET | `/maintenance` | List maintenance requests |

#### Financial
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/financial` | Create financial transaction |
| GET | `/financial` | List financial transactions |

### 📊 Analytics & Reporting

#### Overview Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/overview` | System overview dashboard |
| GET | `/api/analytics/documents` | Document analytics |
| GET | `/api/analytics/processing` | Processing analytics |
| GET | `/api/analytics/data-insights` | Data insights |

#### Property Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/analytics/dashboard` | Property management dashboard |
| GET | `/analytics/property/{property_id}/performance` | Individual property performance |

### ⚙️ Queue Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/jobs` | Create new job |
| POST | `/jobs/batch/process-documents` | Batch process documents |
| GET | `/jobs/{job_id}` | Get job status |
| GET | `/queues/{queue_name}/stats` | Queue statistics |
| GET | `/queues/stats` | All queues statistics |
| POST | `/queues/cleanup` | Cleanup queues |
| POST | `/jobs/{job_id}/cancel` | Cancel specific job |
| GET | `/api/queue/status` | Queue system status |
| GET | `/api/jobs/{job_id}` | Alternative job status endpoint |

## 🎯 Endpoint Usage by Feature

### Document Upload Flow
1. **Upload**: `POST /api/documents/upload`
2. **Check Status**: `GET /api/documents/{document_id}`
3. **Process**: `POST /process/{document_id}`
4. **Get Results**: `GET /processed-data/{document_id}`

### Property Management Flow
1. **Create Property**: `POST /properties`
2. **Add Tenant**: `POST /tenants`
3. **Create Lease**: `POST /leases`
4. **Track Maintenance**: `POST /maintenance`
5. **Record Financials**: `POST /financial`

### Analytics Dashboard Flow
1. **Overview**: `GET /api/analytics/overview`
2. **Property Dashboard**: `GET /analytics/dashboard`
3. **Document Insights**: `GET /api/analytics/documents`
4. **Processing Stats**: `GET /analytics/processing-stats`

## 🔒 Authentication & Security

### Current Implementation
- CORS enabled for frontend (http://localhost:5173, http://localhost:5175)
- No authentication implemented (development mode)

### Production Considerations
- Implement JWT token authentication
- Add role-based access control (RBAC)
- Enable HTTPS
- Add rate limiting
- Implement API key authentication for service-to-service calls

## 📱 Frontend Routes

### Main Application Pages
- **Dashboard**: http://localhost:5175/
- **Properties**: http://localhost:5175/properties
- **Tenants**: http://localhost:5175/tenants
- **Leases**: http://localhost:5175/leases
- **Maintenance**: http://localhost:5175/maintenance
- **Analytics**: http://localhost:5175/analytics
- **Documents**: http://localhost:5175/documents
- **Settings**: http://localhost:5175/settings

## 🛠️ Development & Testing URLs

### API Testing
```bash
# Health check
curl http://localhost:8000/health

# Upload document
curl -X POST -F "file=@document.pdf" http://localhost:8000/api/documents/upload

# Get analytics
curl http://localhost:8000/api/analytics/overview

# Property management
curl http://localhost:8000/properties
```

### Database Access
- **SQLite Database**: `C:\REIMS\reims.db`
- **Database Browser**: Use SQLite Browser or similar tool

### Log Files
- **Backend Logs**: Console output from `python start_optimized_server.py`
- **Frontend Logs**: Browser console (F12)
- **Storage Logs**: MinIO console logs

## 🔄 Environment-Specific URLs

### Development
- Backend: http://localhost:8000
- Frontend: http://localhost:5175
- Storage: http://localhost:9000

### Production (Typical Setup)
- Backend: https://api.reims.company.com
- Frontend: https://reims.company.com
- Storage: https://storage.reims.company.com

### Testing
- Backend: http://localhost:8001
- Frontend: http://localhost:5174
- Storage: http://localhost:9001

## 📊 Monitoring URLs

### System Status
- **Health**: http://localhost:8000/health
- **Queue Status**: http://localhost:8000/api/queue/status
- **Storage Stats**: http://localhost:8000/statistics

### Performance Metrics
- **Processing Stats**: http://localhost:8000/analytics/processing-stats
- **System Overview**: http://localhost:8000/api/analytics/overview
- **Document Analytics**: http://localhost:8000/api/analytics/documents
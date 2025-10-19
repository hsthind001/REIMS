# REIMS Development Guidelines for AI Agents

## Project Overview
REIMS is an enterprise-grade Real Estate Intelligence & Management System with a **hybrid storage architecture** combining PostgreSQL/SQLite databases with MinIO object storage. The system follows a **graceful degradation pattern** - services work in isolation and progressively enhance when dependencies are available.

## Architecture & Service Boundaries

### Core Services (Port Configuration)
- **Backend API**: `localhost:8001` (FastAPI with auto-fallback database)
- **Frontend**: `localhost:5173` (React + Vite)  
- **MinIO Storage**: `localhost:9000` (API) / `localhost:9001` (Console)
- **PostgreSQL**: `localhost:5432` (primary) / SQLite fallback (`reims.db`)

### Key Pattern: Progressive Enhancement
The system is designed to work with **graceful degradation**:
```python
# Pattern found in simple_backend.py
if DATABASE_AVAILABLE and db:
    # Use PostgreSQL/SQLite
    return database_result
# Always fallback to mock data
return mock_data_result
```

## Essential Startup Workflows

### Primary Startup Command
```bash
python start_reims_all.py
```
This is the **single source of truth** for system startup. It handles service orchestration, dependency checking, and verification.

### Service Dependencies
1. **Database** (auto-created via `backend/database.py`)
2. **MinIO** (started via `minio.exe server minio-data`)
3. **Backend** (started via `simple_backend.py`)
4. **Frontend** (started via `npm run dev` in `frontend/`)

### Testing Strategy
- Use `test_*.py` files for component testing
- `verify_*.py` files for integration testing
- Pattern: `test_complete_workflow.py` for end-to-end validation

## Critical File Patterns

### Database Models (`backend/database.py`)
- **Auto-fallback**: PostgreSQL → SQLite 
- **Key Models**: `Document`, `ProcessingJob`, `ExtractedData`, `Property`
- **MinIO Integration**: Built into `Document` model with `minio_*` fields

### API Structure (`backend/api/`)
- **Modular routers**: Each feature has dedicated router file
- **CORS**: Fixed to `localhost:5173` (frontend URL)
- **Health checks**: `/health` endpoint for service verification

### Frontend Architecture (`frontend/src/`)
- **Multiple App variants**: `App.jsx`, `OptimizedWorkingApp.jsx`, `ExecutiveApp*.jsx`
- **Component pattern**: Executive-level components for business users
- **State management**: Local state with `refreshTrigger` pattern for data synchronization

## Storage & Data Flow

### Document Upload Workflow
1. Frontend uploads to `/api/documents/upload`
2. Backend saves to **local storage** (`storage/`) first
3. **Parallel upload** to MinIO if available
4. **Database record** created with both local and MinIO paths
5. **Metadata JSON** stored alongside file

### MinIO Configuration
- **Default bucket**: `reims-documents`
- **Access**: `minioadmin` / `minioadmin`
- **Object naming**: `frontend-uploads/{property_id}/{filename}`

## Development Conventions

### Port Management
- **Never hardcode ports** - use the established configuration
- Check `PORT_CONFIGURATION.md` for service conflicts
- Use `netstat -ano | findstr :PORT` to verify availability

### File Organization
- **Root scripts**: Single-purpose startup/test files
- **Backend**: Modular API structure with shared database
- **Frontend**: Multiple app variants for different use cases
- **Storage**: Hybrid local + MinIO approach

### Error Handling Pattern
```python
try:
    # Primary implementation (database/MinIO)
    return primary_result
except Exception as e:
    print(f"❌ Primary failed: {e}")
    # Always provide fallback
    return fallback_result
```

## Integration Points

### Cross-Service Communication
- **API calls**: Frontend → Backend via `fetch('http://localhost:8001/api/*')`
- **Health monitoring**: Regular `/health` endpoint checks
- **Service discovery**: Port-based with timeout handling

### Data Consistency
- **Document tracking**: Database primary key + MinIO object reference
- **Property relationships**: `property_id` as foreign key across documents
- **Analytics aggregation**: Real-time computation from database

## Common Issues & Solutions

### Startup Problems
- **Port conflicts**: Run `check_ports.ps1` to verify availability
- **Database issues**: Check `reims.db` file permissions and SQLite fallback
- **MinIO connectivity**: Verify `minio.exe` is in root directory

### Development Debugging
- **Backend logs**: Console output shows database/MinIO connection status
- **Frontend debugging**: Use browser DevTools for API call inspection
- **Service verification**: `verify_complete_pipeline.py` for end-to-end testing

## Key Dependencies

### Backend Requirements
- **FastAPI**: Web framework with automatic OpenAPI docs
- **SQLAlchemy**: ORM with PostgreSQL/SQLite support
- **MinIO Python Client**: Object storage integration
- **Uvicorn**: ASGI server (auto-started)

### Frontend Stack
- **React 18**: Component framework
- **Vite**: Build tool with HMR
- **TailwindCSS + shadcn/ui**: Styling system
- **Framer Motion**: Animation library for executive UX

When working on this codebase, always verify service health, use the established startup procedures, and maintain the graceful degradation patterns that make the system resilient.
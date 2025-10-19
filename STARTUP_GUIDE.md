# REIMS System Startup Guide

## 🚀 Quick Start (Recommended)

### 1. Start Backend Server (Optimized)
```powershell
# Navigate to REIMS directory
cd C:\REIMS

# Start the optimized backend server
python start_optimized_server.py
```

This will automatically:
- ✅ Check and install missing dependencies
- ✅ Set up the SQLite database
- ✅ Create necessary directories (uploads, storage)
- ✅ Start all 4 API routers (upload, analytics, property_management, ai_processing)
- ✅ Run health checks

### 2. Start Frontend Development Server
```powershell
# Open a new terminal and navigate to frontend
cd C:\REIMS\frontend

# Install dependencies (first time only)
npm install

# Start the development server
npm run dev
```

### 3. Optional: Start Storage Service (MinIO)
```powershell
# In another terminal
cd C:\REIMS
.\start_storage.ps1
```

## 🌐 System URLs

### Backend Services
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Frontend
- **Frontend Application**: http://localhost:3000

### Storage (Optional)
- **MinIO Storage**: http://localhost:9000
- **MinIO Console**: http://localhost:9001

## 📋 Detailed Startup Process

### Prerequisites
- Python 3.13 installed
- Node.js and npm installed
- PowerShell execution policy allows scripts

### Step-by-Step Startup

#### Backend Server
1. **Open PowerShell as Administrator**
2. **Navigate to REIMS directory**:
   ```powershell
   cd C:\REIMS
   ```

3. **Start the optimized server**:
   ```powershell
   python start_optimized_server.py
   ```

4. **Verify backend is running**:
   ```powershell
   curl http://localhost:8000/health
   ```
   Expected response: `{"status":"healthy"}`

#### Frontend Application
1. **Open a new PowerShell terminal**
2. **Navigate to frontend directory**:
   ```powershell
   cd C:\REIMS\frontend
   ```

3. **Install dependencies** (first time only):
   ```powershell
   npm install
   ```

4. **Start development server**:
   ```powershell
   npm run dev
   ```

5. **Access the application**: Open browser to http://localhost:3000

#### Storage Service (Optional)
1. **Open another PowerShell terminal**
2. **Navigate to REIMS directory**:
   ```powershell
   cd C:\REIMS
   ```

3. **Start MinIO storage**:
   ```powershell
   .\start_storage.ps1
   ```

## 🔧 Alternative Startup Methods

### Manual Backend Startup
If the optimized server doesn't work, use the manual method:

```powershell
# Install dependencies manually
python -m pip install sqlalchemy fastapi uvicorn pandas pymupdf requests httpx minio python-dotenv

# Start with uvicorn directly
python -m uvicorn backend.api.main:app --reload --port 8000
```

### Production Startup
For production deployment:

```powershell
# Backend (production mode)
python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --workers 4

# Frontend (build and serve)
cd frontend
npm run build
npm run start
```

## 🔍 System Health Verification

### Quick Health Check (Recommended)
```powershell
# Complete system status check - checks both backend and frontend
.\check_reims_status.ps1
```

This script provides:
- ✅ Backend status with detailed health information
- ✅ Frontend status with response validation
- ✅ Clear operational status summary
- ✅ No proxy/curl issues

**Note:** We use custom PowerShell scripts to avoid curl alias conflicts. See `POWERSHELL_CURL_FIX.md` for details.

### Backend Health Checks
```powershell
# Quick status check (recommended)
.\check_reims_status.ps1

# Or check manually with Invoke-WebRequest
Invoke-WebRequest -Uri http://localhost:8000/health -UseBasicParsing

# Check API documentation in browser
# Open: http://localhost:8000/docs

# Test specific endpoints
Invoke-WebRequest -Uri http://localhost:8000/api/analytics/overview -UseBasicParsing
```

### Frontend Health Check
- Navigate to http://localhost:3000
- Verify the dashboard loads without errors
- Check browser console for any JavaScript errors

### Database Health Check
```powershell
# Check if database file exists
Test-Path C:\REIMS\reims.db

# Check database tables (if needed)
python -c "from backend.database import engine; from sqlalchemy import inspect; print(inspect(engine).get_table_names())"
```

## 🛑 Shutdown Process

### Graceful Shutdown
1. **Stop Frontend**: `Ctrl+C` in the frontend terminal
2. **Stop Backend**: `Ctrl+C` in the backend terminal
3. **Stop Storage** (if running): `Ctrl+C` in the storage terminal

### Force Shutdown
```powershell
# Kill all related processes
Stop-Process -Name "python" -Force -ErrorAction SilentlyContinue
Stop-Process -Name "node" -Force -ErrorAction SilentlyContinue
Stop-Process -Name "minio" -Force -ErrorAction SilentlyContinue
```

## 📝 Startup Logs

### Successful Backend Startup Log
```
2025-10-07 08:27:48,059 - __main__ - INFO - Starting REIMS Backend Server...
2025-10-07 08:27:49,163 - __main__ - INFO - Server starting with routers: ['upload', 'analytics', 'property_management', 'ai_processing']
2025-10-07 08:27:49,163 - __main__ - INFO - API Documentation: http://localhost:8000/docs
2025-10-07 08:27:49,164 - __main__ - INFO - Health Check: http://localhost:8000/health
INFO:     Started server process [17684]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Successful Frontend Startup Log
```
VITE v4.5.14  ready in 394 ms
➜  Local:   http://localhost:5175/
➜  press h to show help
```

## 🔧 Environment Variables (Optional)

Create a `.env` file in the root directory for custom configuration:

```env
# Database
DATABASE_URL=sqlite:///./reims.db

# Storage
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=password123

# API
API_PORT=8000
FRONTEND_PORT=3000

# Development
DEBUG=True
LOG_LEVEL=INFO
```
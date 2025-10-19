
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import existing routers
try:
    from .upload import router as upload_router
except ImportError:
    upload_router = None

try:
    from .ai_processing import router as ai_router
except ImportError:
    ai_router = None

try:
    from .queue_management import router as queue_router
except ImportError:
    queue_router = None

try:
    from .storage_integration import router as storage_router
except ImportError:
    storage_router = None

try:
    from .dashboard_analytics import router as dashboard_router
except ImportError:
    dashboard_router = None

try:
    from .monitoring import router as monitoring_router
except ImportError:
    monitoring_router = None

try:
    from .kpis import router as kpis_router
except ImportError:
    kpis_router = None

# Import new routers (matching frontend expectations)
from .routes.analytics import router as new_analytics_router
from .routes.properties import router as properties_router
from .routes.documents import router as documents_router
from .routes.alerts import router as alerts_router
from .routes.exit_strategy import router as exit_strategy_router

app = FastAPI(title="REIMS API", description="Real Estate Information Management System API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001",  # Frontend dev server (PRIMARY PORT)
        "http://localhost:3000",  # Alternative port
        "http://localhost:5173",  # Alternative port
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Register new routers (priority - these match frontend expectations)
app.include_router(new_analytics_router)
app.include_router(properties_router)
app.include_router(documents_router)
app.include_router(alerts_router)
app.include_router(exit_strategy_router, prefix="/api/exit-strategy", tags=["exit-strategy"])

# Register existing routers (if available)
# Note: upload_router disabled - using new documents_router instead
# if upload_router:
#     app.include_router(upload_router)
if ai_router:
    app.include_router(ai_router)
if queue_router:
    app.include_router(queue_router)
if storage_router:
    app.include_router(storage_router)
if dashboard_router:
    app.include_router(dashboard_router)
if monitoring_router:
    app.include_router(monitoring_router)
if kpis_router:
    app.include_router(kpis_router)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

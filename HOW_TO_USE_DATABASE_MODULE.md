# How to Use the Database Connection Module in REIMS

**Quick integration guide for the new async PostgreSQL module**

---

## 🚀 Step 1: Environment Setup

Add to your `.env` file (if not already present):

```env
# Database Configuration
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=reims
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password_here

# Optional
ENVIRONMENT=development  # or 'production' for SSL
```

---

## 📝 Step 2: Update Your Main Backend File

### Option A: Modify `start_optimized_server.py`

Add database initialization to your FastAPI app:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.db import init_db, close_db, health_check

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    print("🚀 Starting REIMS application...")
    
    # Initialize database connection pool
    try:
        await init_db()
        print("✅ Database connected")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
    
    yield  # Application runs here
    
    # Cleanup
    print("🛑 Shutting down REIMS...")
    await close_db()
    print("✅ Database connections closed")

# Update your FastAPI app
app = FastAPI(
    title="REIMS API",
    version="2.0",
    lifespan=lifespan  # Add this!
)

# Add health check endpoint
@app.get("/health/database")
async def database_health():
    """Check database health"""
    return await health_check()
```

---

## 🔨 Step 3: Use in Your Routers

### Example: Property Management Router

Create or update `backend/routers/properties.py`:

```python
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from backend.db import fetch_all, fetch_one, fetch_val, execute, QueryError

router = APIRouter(prefix="/api/properties", tags=["properties"])


class Property(BaseModel):
    id: Optional[int] = None
    name: str
    address: str
    city: str
    state: str
    zip_code: str
    property_type: str
    total_units: int
    occupied_units: int = 0


@router.get("/", response_model=List[dict])
async def get_properties():
    """Get all properties"""
    try:
        properties = await fetch_all("""
            SELECT * FROM properties 
            ORDER BY name
        """)
        return [dict(p) for p in properties]
    except QueryError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{property_id}", response_model=dict)
async def get_property(property_id: int):
    """Get property by ID"""
    try:
        property = await fetch_one(
            "SELECT * FROM properties WHERE id = $1",
            property_id
        )
        
        if not property:
            raise HTTPException(status_code=404, detail="Property not found")
        
        return dict(property)
    except QueryError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", status_code=201)
async def create_property(property: Property):
    """Create new property"""
    try:
        property_id = await fetch_val(
            """
            INSERT INTO properties (
                name, address, city, state, zip_code,
                property_type, total_units, occupied_units
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id
            """,
            property.name, property.address, property.city,
            property.state, property.zip_code, property.property_type,
            property.total_units, property.occupied_units
        )
        
        return {"id": property_id, "message": "Property created"}
    except QueryError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{property_id}")
async def update_property(property_id: int, property: Property):
    """Update property"""
    try:
        await execute(
            """
            UPDATE properties
            SET name=$1, address=$2, city=$3, state=$4, 
                zip_code=$5, property_type=$6, total_units=$7,
                occupied_units=$8, updated_at=NOW()
            WHERE id=$9
            """,
            property.name, property.address, property.city,
            property.state, property.zip_code, property.property_type,
            property.total_units, property.occupied_units, property_id
        )
        
        return {"message": "Property updated"}
    except QueryError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{property_id}")
async def delete_property(property_id: int):
    """Delete property"""
    try:
        await execute(
            "DELETE FROM properties WHERE id = $1",
            property_id
        )
        return {"message": "Property deleted"}
    except QueryError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
async def get_property_stats():
    """Get property statistics"""
    try:
        stats = await fetch_one("""
            SELECT 
                COUNT(*) as total_properties,
                SUM(total_units) as total_units,
                SUM(occupied_units) as occupied_units,
                ROUND(AVG(occupied_units::numeric / NULLIF(total_units, 0) * 100), 2) as avg_occupancy
            FROM properties
        """)
        
        return dict(stats)
    except QueryError as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 🔗 Step 4: Register Your Router

In your main backend file:

```python
from backend.routers import properties

# Include the router
app.include_router(properties.router)
```

---

## 🗄️ Step 5: Create Database Tables

Create a migration script `backend/db/create_tables.py`:

```python
"""
Create REIMS database tables
"""
import asyncio
from backend.db import init_db, close_db, execute

async def create_tables():
    """Create all database tables"""
    try:
        await init_db()
        print("Creating tables...")
        
        # Properties table
        await execute("""
            CREATE TABLE IF NOT EXISTS properties (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                address VARCHAR(300) NOT NULL,
                city VARCHAR(100),
                state VARCHAR(2),
                zip_code VARCHAR(10),
                property_type VARCHAR(50),
                total_units INTEGER DEFAULT 0,
                occupied_units INTEGER DEFAULT 0,
                status VARCHAR(20) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        print("✅ Properties table created")
        
        # Tenants table
        await execute("""
            CREATE TABLE IF NOT EXISTS tenants (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                email VARCHAR(200) UNIQUE NOT NULL,
                phone VARCHAR(20),
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        print("✅ Tenants table created")
        
        # Leases table
        await execute("""
            CREATE TABLE IF NOT EXISTS leases (
                id SERIAL PRIMARY KEY,
                property_id INTEGER REFERENCES properties(id) ON DELETE CASCADE,
                tenant_id INTEGER REFERENCES tenants(id) ON DELETE CASCADE,
                unit_number VARCHAR(20),
                monthly_rent DECIMAL(10, 2) NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE,
                status VARCHAR(20) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT NOW(),
                UNIQUE(property_id, tenant_id, status)
            )
        """)
        print("✅ Leases table created")
        
        # Create indexes
        await execute("CREATE INDEX IF NOT EXISTS idx_properties_city ON properties(city)")
        await execute("CREATE INDEX IF NOT EXISTS idx_properties_type ON properties(property_type)")
        await execute("CREATE INDEX IF NOT EXISTS idx_leases_property ON leases(property_id)")
        await execute("CREATE INDEX IF NOT EXISTS idx_leases_tenant ON leases(tenant_id)")
        print("✅ Indexes created")
        
        print("\n🎉 All tables created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
    finally:
        await close_db()

if __name__ == "__main__":
    asyncio.run(create_tables())
```

Run it:
```bash
python backend/db/create_tables.py
```

---

## 📊 Step 6: Test Your Integration

### Test 1: Health Check

```bash
curl http://localhost:8000/health/database
```

Expected response:
```json
{
  "status": "healthy",
  "latency_ms": 12.34,
  "pool_size": 15,
  "pool_free": 10,
  "pool_active": 5,
  "database": "reims",
  "host": "localhost",
  "port": 5432,
  "postgresql_version": "PostgreSQL 15.2"
}
```

### Test 2: Create Property

```bash
curl -X POST http://localhost:8000/api/properties \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sunset Apartments",
    "address": "123 Main St",
    "city": "Los Angeles",
    "state": "CA",
    "zip_code": "90001",
    "property_type": "Residential",
    "total_units": 50,
    "occupied_units": 45
  }'
```

### Test 3: Get All Properties

```bash
curl http://localhost:8000/api/properties
```

### Test 4: Get Property Stats

```bash
curl http://localhost:8000/api/properties/stats/summary
```

---

## 🔄 Step 7: Replace Existing Database Code

If you have existing database code in REIMS, replace it:

### Before (old sync code):
```python
import psycopg2

conn = psycopg2.connect("postgresql://user:pass@localhost/reims")
cursor = conn.cursor()
cursor.execute("SELECT * FROM properties")
properties = cursor.fetchall()
conn.close()
```

### After (new async code):
```python
from backend.db import fetch_all

properties = await fetch_all("SELECT * FROM properties")
```

---

## 🎯 Common Patterns

### Pattern 1: Search with Filters

```python
@router.get("/search")
async def search_properties(
    city: Optional[str] = None,
    property_type: Optional[str] = None,
    limit: int = 20
):
    where_clauses = []
    params = []
    
    if city:
        where_clauses.append(f"city = ${len(params) + 1}")
        params.append(city)
    
    if property_type:
        where_clauses.append(f"property_type = ${len(params) + 1}")
        params.append(property_type)
    
    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    
    params.append(limit)
    
    properties = await fetch_all(
        f"SELECT * FROM properties {where_sql} LIMIT ${len(params)}",
        *params
    )
    
    return [dict(p) for p in properties]
```

### Pattern 2: Transactions

```python
from backend.db import get_connection

@router.post("/transfer-tenant")
async def transfer_tenant(old_property_id: int, new_property_id: int, tenant_id: int):
    async with get_connection() as conn:
        async with conn.transaction():
            # End old lease
            await conn.execute(
                "UPDATE leases SET status='ended', end_date=NOW() WHERE property_id=$1 AND tenant_id=$2",
                old_property_id, tenant_id
            )
            
            # Decrease old property occupancy
            await conn.execute(
                "UPDATE properties SET occupied_units=occupied_units-1 WHERE id=$1",
                old_property_id
            )
            
            # Create new lease
            await conn.execute(
                "INSERT INTO leases (property_id, tenant_id, monthly_rent, start_date) VALUES ($1, $2, $3, NOW())",
                new_property_id, tenant_id, 1500.00
            )
            
            # Increase new property occupancy
            await conn.execute(
                "UPDATE properties SET occupied_units=occupied_units+1 WHERE id=$1",
                new_property_id
            )
    
    return {"message": "Tenant transferred successfully"}
```

### Pattern 3: Aggregations

```python
@router.get("/analytics/revenue")
async def get_revenue_analytics():
    result = await fetch_one("""
        SELECT 
            COUNT(DISTINCT p.id) as total_properties,
            COUNT(l.id) as active_leases,
            SUM(l.monthly_rent) as monthly_revenue,
            AVG(l.monthly_rent) as avg_rent,
            MAX(l.monthly_rent) as max_rent,
            MIN(l.monthly_rent) as min_rent
        FROM properties p
        LEFT JOIN leases l ON p.id = l.property_id AND l.status = 'active'
    """)
    
    return dict(result)
```

---

## 🐛 Troubleshooting

### Error: "Pool not initialized"
**Solution:** Make sure you added the `lifespan` parameter to FastAPI app:
```python
app = FastAPI(lifespan=lifespan)
```

### Error: "Connection failed"
**Solution:** 
1. Check PostgreSQL is running
2. Verify `.env` file has correct DATABASE_PASSWORD
3. Run `python -m backend.db.connection` to test

### Error: "Table does not exist"
**Solution:** Run the table creation script:
```bash
python backend/db/create_tables.py
```

---

## 📚 Documentation

- **Complete Guide:** `DATABASE_CONNECTION_MODULE.md`
- **API Reference:** `backend/db/README.md`
- **Examples:** `backend/db/example_usage.py`
- **This Guide:** `HOW_TO_USE_DATABASE_MODULE.md`

---

## ✅ Checklist

- [ ] Add `.env` file with database credentials
- [ ] Update main backend file with `lifespan`
- [ ] Create database tables
- [ ] Create property router (or update existing)
- [ ] Register router in main app
- [ ] Test health check endpoint
- [ ] Test CRUD operations
- [ ] Replace old database code
- [ ] Add error handling
- [ ] Test transactions

---

## 🚀 You're Ready!

Your REIMS backend now has:
- ✅ Async PostgreSQL connection pool
- ✅ 8 convenient query functions
- ✅ Health monitoring
- ✅ Production-ready error handling
- ✅ FastAPI integration
- ✅ Transaction support

**Start your backend:**
```bash
python start_optimized_server.py
```

**Test database health:**
```bash
curl http://localhost:8000/health/database
```

---

**Happy Coding! 🎉**


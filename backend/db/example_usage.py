"""
REIMS Database Connection Module - Usage Examples

This file demonstrates various ways to use the database connection module
in the REIMS FastAPI backend.

Author: REIMS Development Team
Date: October 12, 2025
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
import asyncpg

# Import database functions
from backend.db import (
    init_db,
    close_db,
    fetch_all,
    fetch_one,
    fetch_val,
    execute,
    get_connection,
    health_check,
    QueryError,
    ConnectionError,
)


# ============================================================================
# EXAMPLE 1: FastAPI Lifespan Management
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage database connection pool lifecycle.
    Initializes on startup, closes on shutdown.
    """
    print("🚀 Starting REIMS application...")
    
    # Startup: Initialize database pool
    try:
        await init_db()
        print("✅ Database connection pool initialized")
    except ConnectionError as e:
        print(f"❌ Failed to initialize database: {e}")
        # You might want to exit here if database is critical
    
    yield  # Application runs here
    
    # Shutdown: Close database pool
    print("🛑 Shutting down REIMS application...")
    await close_db()
    print("✅ Database connection pool closed")


# Create FastAPI app with lifespan
app = FastAPI(
    title="REIMS API",
    version="2.0",
    lifespan=lifespan
)


# ============================================================================
# EXAMPLE 2: Health Check Endpoint
# ============================================================================

@app.get("/health/database")
async def database_health_endpoint():
    """
    Check database health and return connection pool stats.
    """
    return await health_check()


# ============================================================================
# EXAMPLE 3: Simple Query Endpoint
# ============================================================================

class Property(BaseModel):
    """Property model"""
    id: int
    name: str
    address: str
    city: str
    state: str
    zip_code: str
    property_type: str
    total_units: int
    occupied_units: int


@app.get("/properties", response_model=List[dict])
async def get_all_properties():
    """
    Fetch all properties from database.
    """
    try:
        properties = await fetch_all("""
            SELECT 
                id, name, address, city, state, zip_code,
                property_type, total_units, occupied_units
            FROM properties
            ORDER BY name
        """)
        
        # Convert asyncpg.Record to dict
        return [dict(p) for p in properties]
    
    except QueryError as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")


# ============================================================================
# EXAMPLE 4: Parameterized Query with Filters
# ============================================================================

@app.get("/properties/{property_id}")
async def get_property(property_id: int):
    """
    Fetch a single property by ID.
    """
    try:
        property_data = await fetch_one(
            """
            SELECT 
                id, name, address, city, state, zip_code,
                property_type, total_units, occupied_units,
                created_at, updated_at
            FROM properties
            WHERE id = $1
            """,
            property_id
        )
        
        if not property_data:
            raise HTTPException(status_code=404, detail=f"Property {property_id} not found")
        
        return dict(property_data)
    
    except QueryError as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")


# ============================================================================
# EXAMPLE 5: Fetch Single Value (Aggregation)
# ============================================================================

@app.get("/properties/stats/total-units")
async def get_total_units():
    """
    Get total units across all properties.
    """
    try:
        total = await fetch_val("""
            SELECT SUM(total_units) 
            FROM properties
        """)
        
        return {
            "total_units": total or 0,
            "description": "Total units across all properties"
        }
    
    except QueryError as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# EXAMPLE 6: INSERT with execute()
# ============================================================================

class PropertyCreate(BaseModel):
    """Property creation model"""
    name: str
    address: str
    city: str
    state: str
    zip_code: str
    property_type: str
    total_units: int


@app.post("/properties", status_code=201)
async def create_property(property: PropertyCreate):
    """
    Create a new property.
    """
    try:
        # Insert and return the new ID
        property_id = await fetch_val(
            """
            INSERT INTO properties (
                name, address, city, state, zip_code,
                property_type, total_units, occupied_units
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, 0)
            RETURNING id
            """,
            property.name,
            property.address,
            property.city,
            property.state,
            property.zip_code,
            property.property_type,
            property.total_units
        )
        
        return {
            "id": property_id,
            "message": "Property created successfully"
        }
    
    except QueryError as e:
        raise HTTPException(status_code=500, detail=f"Failed to create property: {str(e)}")


# ============================================================================
# EXAMPLE 7: UPDATE with execute()
# ============================================================================

class PropertyUpdate(BaseModel):
    """Property update model"""
    occupied_units: Optional[int] = None
    total_units: Optional[int] = None


@app.patch("/properties/{property_id}")
async def update_property(property_id: int, update: PropertyUpdate):
    """
    Update property details.
    """
    try:
        # Build dynamic update query
        updates = []
        params = []
        param_idx = 1
        
        if update.occupied_units is not None:
            updates.append(f"occupied_units = ${param_idx}")
            params.append(update.occupied_units)
            param_idx += 1
        
        if update.total_units is not None:
            updates.append(f"total_units = ${param_idx}")
            params.append(update.total_units)
            param_idx += 1
        
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        params.append(property_id)
        
        query = f"""
            UPDATE properties
            SET {', '.join(updates)}, updated_at = NOW()
            WHERE id = ${param_idx}
        """
        
        await execute(query, *params)
        
        return {"message": "Property updated successfully"}
    
    except QueryError as e:
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")


# ============================================================================
# EXAMPLE 8: DELETE with execute()
# ============================================================================

@app.delete("/properties/{property_id}")
async def delete_property(property_id: int):
    """
    Delete a property.
    """
    try:
        # Check if exists
        exists = await fetch_val(
            "SELECT EXISTS(SELECT 1 FROM properties WHERE id = $1)",
            property_id
        )
        
        if not exists:
            raise HTTPException(status_code=404, detail=f"Property {property_id} not found")
        
        # Delete
        await execute(
            "DELETE FROM properties WHERE id = $1",
            property_id
        )
        
        return {"message": f"Property {property_id} deleted successfully"}
    
    except QueryError as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


# ============================================================================
# EXAMPLE 9: Transaction with Context Manager
# ============================================================================

@app.post("/properties/{property_id}/lease")
async def create_lease(property_id: int, tenant_id: int, monthly_rent: float):
    """
    Create a lease and update occupied units (transaction).
    """
    try:
        async with get_connection() as conn:
            # Start transaction
            async with conn.transaction():
                # Insert lease
                lease_id = await conn.fetchval(
                    """
                    INSERT INTO leases (property_id, tenant_id, monthly_rent, start_date)
                    VALUES ($1, $2, $3, CURRENT_DATE)
                    RETURNING id
                    """,
                    property_id, tenant_id, monthly_rent
                )
                
                # Update occupied units
                await conn.execute(
                    """
                    UPDATE properties
                    SET occupied_units = occupied_units + 1
                    WHERE id = $1
                    """,
                    property_id
                )
                
                return {
                    "lease_id": lease_id,
                    "message": "Lease created and property updated"
                }
    
    except asyncpg.UniqueViolationError:
        raise HTTPException(status_code=400, detail="Tenant already has a lease at this property")
    
    except QueryError as e:
        raise HTTPException(status_code=500, detail=f"Transaction failed: {str(e)}")


# ============================================================================
# EXAMPLE 10: Complex Query with JOINs
# ============================================================================

@app.get("/properties/{property_id}/analytics")
async def get_property_analytics(property_id: int):
    """
    Get comprehensive property analytics with related data.
    """
    try:
        analytics = await fetch_one(
            """
            SELECT 
                p.id,
                p.name,
                p.total_units,
                p.occupied_units,
                ROUND((p.occupied_units::numeric / NULLIF(p.total_units, 0)) * 100, 2) as occupancy_rate,
                COUNT(DISTINCT l.id) as total_leases,
                COUNT(DISTINCT t.id) as total_tenants,
                COALESCE(SUM(l.monthly_rent), 0) as total_monthly_revenue,
                COALESCE(AVG(l.monthly_rent), 0) as avg_rent_per_unit
            FROM properties p
            LEFT JOIN leases l ON p.id = l.property_id AND l.status = 'active'
            LEFT JOIN tenants t ON l.tenant_id = t.id
            WHERE p.id = $1
            GROUP BY p.id, p.name, p.total_units, p.occupied_units
            """,
            property_id
        )
        
        if not analytics:
            raise HTTPException(status_code=404, detail=f"Property {property_id} not found")
        
        return dict(analytics)
    
    except QueryError as e:
        raise HTTPException(status_code=500, detail=f"Analytics query failed: {str(e)}")


# ============================================================================
# EXAMPLE 11: Batch Operations
# ============================================================================

@app.post("/properties/bulk-update-status")
async def bulk_update_status(property_ids: List[int], new_status: str):
    """
    Update status for multiple properties at once.
    """
    try:
        # Use ANY() for efficient bulk update
        result = await execute(
            """
            UPDATE properties
            SET status = $1, updated_at = NOW()
            WHERE id = ANY($2::int[])
            """,
            new_status,
            property_ids
        )
        
        return {
            "message": f"Updated status for {len(property_ids)} properties",
            "result": result
        }
    
    except QueryError as e:
        raise HTTPException(status_code=500, detail=f"Bulk update failed: {str(e)}")


# ============================================================================
# EXAMPLE 12: Search with Pagination
# ============================================================================

@app.get("/properties/search")
async def search_properties(
    query: Optional[str] = None,
    city: Optional[str] = None,
    property_type: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    """
    Search properties with filters and pagination.
    """
    try:
        # Build dynamic WHERE clause
        where_clauses = []
        params = []
        param_idx = 1
        
        if query:
            where_clauses.append(f"(name ILIKE ${param_idx} OR address ILIKE ${param_idx})")
            params.append(f"%{query}%")
            param_idx += 1
        
        if city:
            where_clauses.append(f"city = ${param_idx}")
            params.append(city)
            param_idx += 1
        
        if property_type:
            where_clauses.append(f"property_type = ${param_idx}")
            params.append(property_type)
            param_idx += 1
        
        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        # Add pagination params
        params.extend([limit, offset])
        
        # Execute query
        properties = await fetch_all(
            f"""
            SELECT 
                id, name, address, city, state, property_type,
                total_units, occupied_units
            FROM properties
            {where_sql}
            ORDER BY name
            LIMIT ${param_idx} OFFSET ${param_idx + 1}
            """,
            *params
        )
        
        # Get total count
        total = await fetch_val(
            f"SELECT COUNT(*) FROM properties {where_sql}",
            *params[:-2]  # Exclude limit/offset
        )
        
        return {
            "properties": [dict(p) for p in properties],
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total
        }
    
    except QueryError as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


# ============================================================================
# Main Entry Point (for testing)
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("Starting REIMS API with database connection examples...")
    print("API docs available at: http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

















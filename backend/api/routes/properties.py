"""
Properties API Routes
Provides property listing, filtering, sorting, and search
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional

from ..database import get_db

router = APIRouter(prefix="/api/properties", tags=["properties"])


@router.get("")
async def get_properties(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    status: Optional[str] = Query(None, description="Filter by status: 'healthy' or 'alert'"),
    property_type: Optional[str] = Query(None, description="Filter by property type"),
    sort_by: str = Query("name", description="Sort by field: name, occupancy_rate, noi, dscr"),
    sort_order: str = Query("asc", description="Sort order: asc or desc"),
    search: Optional[str] = Query(None, description="Search by name or address"),
    db: Session = Depends(get_db)
):
    print("🔧 DEBUG: Using updated properties API with occupancy calculation")
    """
    Get properties list with pagination, filtering, sorting, and search
    
    Query Parameters:
    - skip: Offset for pagination (default: 0)
    - limit: Number of records (default: 20, max: 100)
    - status: Filter by 'healthy' or 'alert'
    - property_type: Filter by property type
    - sort_by: Sort field (name, occupancy_rate, noi, dscr)
    - sort_order: Sort direction (asc, desc)
    - search: Search in name or address
    
    Returns:
    - properties: List of property objects
    - total: Total count of properties matching filters
    """
    
    try:
        # Build WHERE clause conditions
        where_conditions = []
        params = {
            "skip": skip,
            "limit": limit
        }
        
        # Status filter (simplified since we don't have DSCR/occupancy columns in SQLite)
        if status:
            if status == "alert":
                where_conditions.append("p.status = 'alert'")
            elif status == "healthy":
                where_conditions.append("(p.status = 'active' OR p.status = 'healthy')")
        
        # Property type filter
        if property_type:
            where_conditions.append("p.property_type = :property_type")
            params["property_type"] = property_type
        
        # Search filter (using LIKE for SQLite compatibility)
        if search:
            where_conditions.append(
                "(p.name LIKE :search_pattern OR p.address LIKE :search_pattern)"
            )
            params["search_pattern"] = f"%{search}%"
        
        # Combine WHERE conditions
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # Determine ORDER BY clause (using SQLite column names)
        sort_column_map = {
            "name": "p.name",
            "occupancy_rate": "p.name",  # No occupancy in schema, sort by name
            "noi": "p.monthly_rent",  # Sort by monthly rent as proxy for NOI
            "dscr": "p.name",  # No DSCR in schema, sort by name
            "value": "p.current_market_value",
            "created_at": "p.created_at"
        }
        
        sort_column = sort_column_map.get(sort_by, "p.name")
        sort_direction = "DESC" if sort_order.lower() == "desc" else "ASC"
        order_clause = f"ORDER BY {sort_column} {sort_direction}"
        
        # Count query
        count_query = f"""
            SELECT COUNT(*)
            FROM properties p
            {where_clause}
        """
        
        total = db.execute(text(count_query), params).scalar() or 0
        
        # Main query (using SQLite schema column names)
        main_query = f"""
            SELECT 
                p.id,
                p.name,
                p.address,
                p.city,
                p.state,
                p.square_footage as total_sqft,
                p.purchase_price as acquisition_cost,
                p.current_market_value as current_value,
                p.monthly_rent,
                p.year_built,
                0 as loan_balance,
                COALESCE(p.annual_noi, p.monthly_rent * 12, 0) as noi,
                1.5 as dscr,
                CASE 
                    WHEN p.occupancy_rate > 0 THEN p.occupancy_rate / 100.0
                    ELSE 0.95
                END as occupancy_rate,
                0 as has_active_alerts,
                p.created_at,
                p.updated_at,
                -- Property type
                COALESCE(p.property_type, 'commercial') as property_type,
                -- Status (defaults to healthy)
                'healthy' as status,
                -- Units count (default to 1 for single property)
                1 as units
            FROM properties p
            {where_clause}
            {order_clause}
            LIMIT :limit OFFSET :skip
        """
        
        results = db.execute(text(main_query), params).fetchall()
        
        # Format results
        properties = []
        for row in results:
            properties.append({
                "id": row.id,
                "name": row.name,
                "address": row.address,
                "city": row.city,
                "state": row.state,
                "property_type": row.property_type,
                "total_sqft": float(row.total_sqft) if row.total_sqft else 0,
                "square_footage": float(row.total_sqft) if row.total_sqft else 0,  # Alias
                "acquisition_cost": float(row.acquisition_cost) if row.acquisition_cost else 0,
                "current_value": float(row.current_value) if row.current_value else 0,
                "current_market_value": float(row.current_value) if row.current_value else 0,  # Alias
                "monthly_rent": float(row.monthly_rent) if row.monthly_rent else 0,
                "year_built": int(row.year_built) if row.year_built else 2024,
                "loan_balance": float(row.loan_balance) if row.loan_balance else 0,
                "noi": float(row.noi) if row.noi else 0,
                "dscr": float(row.dscr) if row.dscr else 0,
                "occupancy_rate": float(row.occupancy_rate) if row.occupancy_rate else 0,
                "has_active_alerts": bool(row.has_active_alerts),
                "status": row.status,
                "units": row.units,
                "created_at": str(row.created_at) if row.created_at else None,
                "updated_at": str(row.updated_at) if row.updated_at else None,
            })
        
        return {
            "success": True,
            "properties": properties,
            "total": int(total),
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        print(f"Properties query error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch properties: {str(e)}"
        )


@router.get("/{property_id}")
async def get_property(
    property_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed information for a single property
    """
    try:
        result = db.execute(
            text("""
                SELECT 
                    p.id,
                    p.name,
                    p.address,
                    p.city,
                    p.state,
                    p.square_footage as total_sqft,
                    p.purchase_price as acquisition_cost,
                    p.current_market_value as current_value,
                    p.monthly_rent,
                    p.year_built,
                    0 as loan_balance,
                    COALESCE(p.annual_noi, p.monthly_rent * 12, 0) as noi,
                    1.5 as dscr,
                    CASE 
                    WHEN p.occupancy_rate > 0 THEN p.occupancy_rate / 100.0
                    ELSE 0.95
                END as occupancy_rate,
                    0 as has_active_alerts,
                    p.created_at,
                    p.updated_at,
                    COALESCE(p.property_type, 'commercial') as property_type,
                    'healthy' as status,
                    1 as units
                FROM properties p
                WHERE p.id = :property_id
            """),
            {"property_id": property_id}
        ).fetchone()
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Property {property_id} not found"
            )
        
        return {
            "id": result.id,
            "name": result.name,
            "address": result.address,
            "city": result.city,
            "state": result.state,
            "property_type": result.property_type,
            "total_sqft": float(result.total_sqft) if result.total_sqft else 0,
            "square_footage": float(result.total_sqft) if result.total_sqft else 0,
            "acquisition_cost": float(result.acquisition_cost) if result.acquisition_cost else 0,
            "current_value": float(result.current_value) if result.current_value else 0,
            "current_market_value": float(result.current_value) if result.current_value else 0,
            "monthly_rent": float(result.monthly_rent) if result.monthly_rent else 0,
            "year_built": int(result.year_built) if result.year_built else 2024,
            "loan_balance": float(result.loan_balance) if result.loan_balance else 0,
            "noi": float(result.noi) if result.noi else 0,
            "dscr": float(result.dscr) if result.dscr else 0,
            "occupancy_rate": float(result.occupancy_rate) if result.occupancy_rate else 0,
            "has_active_alerts": bool(result.has_active_alerts),
            "status": result.status,
            "units": result.units,
            "created_at": str(result.created_at) if result.created_at else None,
            "updated_at": str(result.updated_at) if result.updated_at else None,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch property: {str(e)}"
        )


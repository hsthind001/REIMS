"""
REIMS Property Management API
Comprehensive property, lease, tenant, and maintenance management endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, timedelta
import uuid

from ..database import get_db
try:
    from ..models.property_models import (
        Property, Tenant, Lease, RentPayment, MaintenanceRequest, 
        FinancialTransaction, PropertyDocument, PropertyType, 
        PropertyStatus, LeaseStatus, MaintenanceStatus, MaintenancePriority
    )
except ImportError:
    # Fallback for direct execution
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from models.property_models import (
        Property, Tenant, Lease, RentPayment, MaintenanceRequest, 
        FinancialTransaction, PropertyDocument, PropertyType, 
        PropertyStatus, LeaseStatus, MaintenanceStatus, MaintenancePriority
    )
from pydantic import BaseModel, Field


# Pydantic schemas for API requests/responses
class PropertyBase(BaseModel):
    property_code: str
    name: str
    address: str
    city: str
    state: str
    zip_code: str
    country: str = "USA"
    property_type: PropertyType
    status: PropertyStatus = PropertyStatus.AVAILABLE
    square_footage: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    parking_spaces: int = 0
    monthly_rent: Optional[float] = None
    description: Optional[str] = None


class PropertyCreate(PropertyBase):
    purchase_price: Optional[float] = None
    current_market_value: Optional[float] = None
    property_taxes: Optional[float] = None
    insurance_cost: Optional[float] = None
    amenities: Optional[str] = None
    year_built: Optional[int] = None


class PropertyResponse(PropertyBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TenantBase(BaseModel):
    tenant_code: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None


class TenantCreate(TenantBase):
    employer: Optional[str] = None
    monthly_income: Optional[float] = None
    credit_score: Optional[int] = None
    date_of_birth: Optional[date] = None
    ssn_last_four: Optional[str] = None


class TenantResponse(TenantBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class LeaseBase(BaseModel):
    lease_number: str
    property_id: int
    tenant_id: int
    start_date: date
    end_date: date
    monthly_rent: float
    security_deposit: float
    late_fee: float = 0.0
    pet_deposit: float = 0.0
    lease_type: str = "fixed_term"
    auto_renewal: bool = False
    notice_period_days: int = 30
    rent_due_day: int = 1


class LeaseCreate(LeaseBase):
    utilities_included: Optional[str] = None
    additional_fees: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    special_provisions: Optional[str] = None


class LeaseResponse(LeaseBase):
    id: int
    status: LeaseStatus
    created_at: datetime
    
    class Config:
        from_attributes = True


class MaintenanceRequestBase(BaseModel):
    request_number: str
    property_id: int
    title: str
    description: str
    category: Optional[str] = None
    priority: MaintenancePriority = MaintenancePriority.MEDIUM


class MaintenanceRequestCreate(MaintenanceRequestBase):
    tenant_id: Optional[int] = None
    estimated_cost: Optional[float] = None


class MaintenanceRequestResponse(MaintenanceRequestBase):
    id: int
    tenant_id: Optional[int]
    status: MaintenanceStatus
    assigned_to: Optional[str]
    reported_date: datetime
    estimated_cost: Optional[float]
    actual_cost: Optional[float]
    
    class Config:
        from_attributes = True


class FinancialTransactionBase(BaseModel):
    transaction_number: str
    property_id: int
    transaction_type: str
    category: str
    amount: float
    description: str
    transaction_date: date


class FinancialTransactionCreate(FinancialTransactionBase):
    payment_method: Optional[str] = None
    vendor: Optional[str] = None
    invoice_number: Optional[str] = None
    tax_deductible: bool = False


class FinancialTransactionResponse(FinancialTransactionBase):
    id: int
    payment_method: Optional[str]
    vendor: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Create router
router = APIRouter(prefix="/property", tags=["Property Management"])


# Property endpoints
@router.post("/properties", response_model=PropertyResponse)
async def create_property(property_data: PropertyCreate, db: Session = Depends(get_db)):
    """Create a new property"""
    try:
        property_obj = Property(**property_data.dict())
        db.add(property_obj)
        db.commit()
        db.refresh(property_obj)
        return property_obj
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating property: {str(e)}")


@router.get("/properties", response_model=List[PropertyResponse])
async def get_properties(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    property_type: Optional[PropertyType] = None,
    status: Optional[PropertyStatus] = None,
    city: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get properties with optional filtering"""
    try:
        query = db.query(Property)
        
        if property_type:
            query = query.filter(Property.property_type == property_type)
        if status:
            query = query.filter(Property.status == status)
        if city:
            query = query.filter(Property.city.ilike(f"%{city}%"))
        
        properties = query.offset(skip).limit(limit).all()
        return properties
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving properties: {str(e)}")


@router.get("/properties/{property_id}", response_model=PropertyResponse)
async def get_property(property_id: int = Path(..., gt=0), db: Session = Depends(get_db)):
    """Get a specific property by ID"""
    try:
        property_obj = db.query(Property).filter(Property.id == property_id).first()
        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found")
        return property_obj
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving property: {str(e)}")


@router.put("/properties/{property_id}", response_model=PropertyResponse)
async def update_property(
    property_id: int,
    property_data: PropertyCreate,
    db: Session = Depends(get_db)
):
    """Update a property"""
    try:
        property_obj = db.query(Property).filter(Property.id == property_id).first()
        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found")
        
        for key, value in property_data.dict(exclude_unset=True).items():
            setattr(property_obj, key, value)
        
        property_obj.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(property_obj)
        return property_obj
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error updating property: {str(e)}")


# Tenant endpoints
@router.post("/tenants", response_model=TenantResponse)
async def create_tenant(tenant_data: TenantCreate, db: Session = Depends(get_db)):
    """Create a new tenant"""
    try:
        tenant_obj = Tenant(**tenant_data.dict())
        db.add(tenant_obj)
        db.commit()
        db.refresh(tenant_obj)
        return tenant_obj
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating tenant: {str(e)}")


@router.get("/tenants", response_model=List[TenantResponse])
async def get_tenants(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get tenants with optional search"""
    try:
        query = db.query(Tenant)
        
        if search:
            query = query.filter(
                (Tenant.first_name.ilike(f"%{search}%")) |
                (Tenant.last_name.ilike(f"%{search}%")) |
                (Tenant.email.ilike(f"%{search}%"))
            )
        
        tenants = query.offset(skip).limit(limit).all()
        return tenants
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving tenants: {str(e)}")


# Lease endpoints
@router.post("/leases", response_model=LeaseResponse)
async def create_lease(lease_data: LeaseCreate, db: Session = Depends(get_db)):
    """Create a new lease"""
    try:
        # Verify property and tenant exist
        property_obj = db.query(Property).filter(Property.id == lease_data.property_id).first()
        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found")
        
        tenant_obj = db.query(Tenant).filter(Tenant.id == lease_data.tenant_id).first()
        if not tenant_obj:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        lease_obj = Lease(**lease_data.dict())
        db.add(lease_obj)
        db.commit()
        db.refresh(lease_obj)
        return lease_obj
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating lease: {str(e)}")


@router.get("/leases", response_model=List[LeaseResponse])
async def get_leases(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    property_id: Optional[int] = None,
    tenant_id: Optional[int] = None,
    status: Optional[LeaseStatus] = None,
    db: Session = Depends(get_db)
):
    """Get leases with optional filtering"""
    try:
        query = db.query(Lease)
        
        if property_id:
            query = query.filter(Lease.property_id == property_id)
        if tenant_id:
            query = query.filter(Lease.tenant_id == tenant_id)
        if status:
            query = query.filter(Lease.status == status)
        
        leases = query.offset(skip).limit(limit).all()
        return leases
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving leases: {str(e)}")


# Maintenance endpoints
@router.post("/maintenance", response_model=MaintenanceRequestResponse)
async def create_maintenance_request(
    request_data: MaintenanceRequestCreate,
    db: Session = Depends(get_db)
):
    """Create a new maintenance request"""
    try:
        # Verify property exists
        property_obj = db.query(Property).filter(Property.id == request_data.property_id).first()
        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found")
        
        # If tenant_id provided, verify tenant exists
        if request_data.tenant_id:
            tenant_obj = db.query(Tenant).filter(Tenant.id == request_data.tenant_id).first()
            if not tenant_obj:
                raise HTTPException(status_code=404, detail="Tenant not found")
        
        maintenance_obj = MaintenanceRequest(**request_data.dict())
        db.add(maintenance_obj)
        db.commit()
        db.refresh(maintenance_obj)
        return maintenance_obj
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating maintenance request: {str(e)}")


@router.get("/maintenance", response_model=List[MaintenanceRequestResponse])
async def get_maintenance_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    property_id: Optional[int] = None,
    status: Optional[MaintenanceStatus] = None,
    priority: Optional[MaintenancePriority] = None,
    db: Session = Depends(get_db)
):
    """Get maintenance requests with optional filtering"""
    try:
        query = db.query(MaintenanceRequest)
        
        if property_id:
            query = query.filter(MaintenanceRequest.property_id == property_id)
        if status:
            query = query.filter(MaintenanceRequest.status == status)
        if priority:
            query = query.filter(MaintenanceRequest.priority == priority)
        
        requests = query.offset(skip).limit(limit).all()
        return requests
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving maintenance requests: {str(e)}")


# Financial endpoints
@router.post("/financial", response_model=FinancialTransactionResponse)
async def create_financial_transaction(
    transaction_data: FinancialTransactionCreate,
    db: Session = Depends(get_db)
):
    """Create a new financial transaction"""
    try:
        # Verify property exists
        property_obj = db.query(Property).filter(Property.id == transaction_data.property_id).first()
        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found")
        
        transaction_obj = FinancialTransaction(**transaction_data.dict())
        db.add(transaction_obj)
        db.commit()
        db.refresh(transaction_obj)
        return transaction_obj
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating financial transaction: {str(e)}")


@router.get("/financial", response_model=List[FinancialTransactionResponse])
async def get_financial_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    property_id: Optional[int] = None,
    transaction_type: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get financial transactions with optional filtering"""
    try:
        query = db.query(FinancialTransaction)
        
        if property_id:
            query = query.filter(FinancialTransaction.property_id == property_id)
        if transaction_type:
            query = query.filter(FinancialTransaction.transaction_type == transaction_type)
        if start_date:
            query = query.filter(FinancialTransaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(FinancialTransaction.transaction_date <= end_date)
        
        transactions = query.offset(skip).limit(limit).all()
        return transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving financial transactions: {str(e)}")


# Analytics and reporting endpoints
@router.get("/analytics/dashboard")
async def get_property_dashboard(db: Session = Depends(get_db)):
    """Get property management dashboard analytics"""
    try:
        # Property statistics
        total_properties = db.query(Property).count()
        occupied_properties = db.query(Property).filter(Property.status == PropertyStatus.OCCUPIED).count()
        available_properties = db.query(Property).filter(Property.status == PropertyStatus.AVAILABLE).count()
        maintenance_properties = db.query(Property).filter(Property.status == PropertyStatus.MAINTENANCE).count()
        
        # Lease statistics
        active_leases = db.query(Lease).filter(Lease.status == LeaseStatus.ACTIVE).count()
        expiring_leases = db.query(Lease).filter(
            Lease.status == LeaseStatus.ACTIVE,
            Lease.end_date <= datetime.utcnow() + timedelta(days=30)
        ).count()
        
        # Maintenance statistics
        pending_maintenance = db.query(MaintenanceRequest).filter(
            MaintenanceRequest.status == MaintenanceStatus.PENDING
        ).count()
        urgent_maintenance = db.query(MaintenanceRequest).filter(
            MaintenanceRequest.priority == MaintenancePriority.URGENT,
            MaintenanceRequest.status.in_([MaintenanceStatus.PENDING, MaintenanceStatus.IN_PROGRESS])
        ).count()
        
        # Financial statistics
        from sqlalchemy import func
        monthly_revenue = db.query(func.sum(Lease.monthly_rent)).filter(
            Lease.status == LeaseStatus.ACTIVE
        ).scalar() or 0
        
        return {
            "properties": {
                "total": total_properties,
                "occupied": occupied_properties,
                "available": available_properties,
                "maintenance": maintenance_properties,
                "occupancy_rate": round((occupied_properties / total_properties * 100) if total_properties > 0 else 0, 1)
            },
            "leases": {
                "active": active_leases,
                "expiring_soon": expiring_leases
            },
            "maintenance": {
                "pending": pending_maintenance,
                "urgent": urgent_maintenance
            },
            "financial": {
                "monthly_revenue": float(monthly_revenue),
                "currency": "USD"
            },
            "generated_at": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating dashboard analytics: {str(e)}")


# Property performance endpoint
@router.get("/analytics/property/{property_id}/performance")
async def get_property_performance(property_id: int, db: Session = Depends(get_db)):
    """Get detailed performance analytics for a specific property"""
    try:
        property_obj = db.query(Property).filter(Property.id == property_id).first()
        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found")
        
        # Calculate metrics
        from sqlalchemy import func
        
        # Revenue metrics
        total_revenue = db.query(func.sum(FinancialTransaction.amount)).filter(
            FinancialTransaction.property_id == property_id,
            FinancialTransaction.transaction_type == "income"
        ).scalar() or 0
        
        total_expenses = db.query(func.sum(FinancialTransaction.amount)).filter(
            FinancialTransaction.property_id == property_id,
            FinancialTransaction.transaction_type == "expense"
        ).scalar() or 0
        
        # Maintenance metrics
        maintenance_count = db.query(MaintenanceRequest).filter(
            MaintenanceRequest.property_id == property_id
        ).count()
        
        maintenance_cost = db.query(func.sum(MaintenanceRequest.actual_cost)).filter(
            MaintenanceRequest.property_id == property_id,
            MaintenanceRequest.actual_cost.isnot(None)
        ).scalar() or 0
        
        return {
            "property_id": property_id,
            "property_name": property_obj.name,
            "financial": {
                "total_revenue": float(total_revenue),
                "total_expenses": float(total_expenses),
                "net_income": float(total_revenue - total_expenses),
                "current_rent": float(property_obj.monthly_rent or 0)
            },
            "maintenance": {
                "total_requests": maintenance_count,
                "total_cost": float(maintenance_cost),
                "average_cost": float(maintenance_cost / maintenance_count) if maintenance_count > 0 else 0
            },
            "occupancy": {
                "status": property_obj.status.value,
                "square_footage": float(property_obj.square_footage or 0)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating property performance: {str(e)}")
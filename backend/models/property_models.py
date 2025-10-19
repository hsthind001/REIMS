"""
REIMS Property Management Models
Comprehensive property, lease, tenant, and maintenance management models
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import DECIMAL
from datetime import datetime
from decimal import Decimal
import enum

Base = declarative_base()


class PropertyType(enum.Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    MIXED_USE = "mixed_use"
    LAND = "land"


class PropertyStatus(enum.Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    MAINTENANCE = "maintenance"
    UNAVAILABLE = "unavailable"


class LeaseStatus(enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    PENDING = "pending"


class MaintenanceStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MaintenancePriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Property(Base):
    """Property model for real estate management"""
    __tablename__ = 'properties'

    id = Column(Integer, primary_key=True)
    property_code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(50), nullable=False)
    zip_code = Column(String(20), nullable=False)
    country = Column(String(100), default="USA")
    
    # Property details
    property_type = Column(Enum(PropertyType), nullable=False)
    status = Column(Enum(PropertyStatus), default=PropertyStatus.AVAILABLE)
    square_footage = Column(DECIMAL(10, 2))
    bedrooms = Column(Integer)
    bathrooms = Column(DECIMAL(3, 1))
    parking_spaces = Column(Integer, default=0)
    
    # Financial information
    purchase_price = Column(DECIMAL(12, 2))
    current_market_value = Column(DECIMAL(12, 2))
    monthly_rent = Column(DECIMAL(10, 2))
    property_taxes = Column(DECIMAL(10, 2))
    insurance_cost = Column(DECIMAL(10, 2))
    
    # Metadata
    description = Column(Text)
    amenities = Column(Text)  # JSON string of amenities
    year_built = Column(Integer)
    last_renovation = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    leases = relationship("Lease", back_populates="property", cascade="all, delete-orphan")
    maintenance_requests = relationship("MaintenanceRequest", back_populates="property")
    financial_transactions = relationship("FinancialTransaction", back_populates="property")


class Tenant(Base):
    """Tenant model for managing renters"""
    __tablename__ = 'tenants'

    id = Column(Integer, primary_key=True)
    tenant_code = Column(String(50), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20))
    
    # Emergency contact
    emergency_contact_name = Column(String(200))
    emergency_contact_phone = Column(String(20))
    emergency_contact_relationship = Column(String(100))
    
    # Background information
    employer = Column(String(200))
    monthly_income = Column(DECIMAL(10, 2))
    credit_score = Column(Integer)
    background_check_status = Column(String(50))
    
    # Metadata
    date_of_birth = Column(DateTime)
    ssn_last_four = Column(String(4))  # Store only last 4 digits for security
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    leases = relationship("Lease", back_populates="tenant")
    maintenance_requests = relationship("MaintenanceRequest", back_populates="tenant")


class Lease(Base):
    """Lease agreement model"""
    __tablename__ = 'leases'

    id = Column(Integer, primary_key=True)
    lease_number = Column(String(50), unique=True, nullable=False)
    property_id = Column(Integer, ForeignKey('properties.id'), nullable=False)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False)
    
    # Lease terms
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    monthly_rent = Column(DECIMAL(10, 2), nullable=False)
    security_deposit = Column(DECIMAL(10, 2), nullable=False)
    late_fee = Column(DECIMAL(8, 2), default=0)
    pet_deposit = Column(DECIMAL(8, 2), default=0)
    
    # Lease status and terms
    status = Column(Enum(LeaseStatus), default=LeaseStatus.PENDING)
    lease_type = Column(String(50), default="fixed_term")  # fixed_term, month_to_month
    auto_renewal = Column(Boolean, default=False)
    notice_period_days = Column(Integer, default=30)
    
    # Financial terms
    rent_due_day = Column(Integer, default=1)  # Day of month rent is due
    utilities_included = Column(Text)  # JSON string of included utilities
    additional_fees = Column(Text)  # JSON string of additional fees
    
    # Metadata
    terms_and_conditions = Column(Text)
    special_provisions = Column(Text)
    signed_date = Column(DateTime)
    move_in_date = Column(DateTime)
    move_out_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    property = relationship("Property", back_populates="leases")
    tenant = relationship("Tenant", back_populates="leases")
    rent_payments = relationship("RentPayment", back_populates="lease")


class RentPayment(Base):
    """Rent payment tracking model"""
    __tablename__ = 'rent_payments'

    id = Column(Integer, primary_key=True)
    lease_id = Column(Integer, ForeignKey('leases.id'), nullable=False)
    payment_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    amount_due = Column(DECIMAL(10, 2), nullable=False)
    amount_paid = Column(DECIMAL(10, 2), nullable=False)
    
    # Payment details
    payment_method = Column(String(50))  # check, bank_transfer, credit_card, cash
    transaction_id = Column(String(100))
    late_fee = Column(DECIMAL(8, 2), default=0)
    is_late = Column(Boolean, default=False)
    is_partial = Column(Boolean, default=False)
    
    # Metadata
    notes = Column(Text)
    processed_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    lease = relationship("Lease", back_populates="rent_payments")


class MaintenanceRequest(Base):
    """Maintenance request and work order management"""
    __tablename__ = 'maintenance_requests'

    id = Column(Integer, primary_key=True)
    request_number = Column(String(50), unique=True, nullable=False)
    property_id = Column(Integer, ForeignKey('properties.id'), nullable=False)
    tenant_id = Column(Integer, ForeignKey('tenants.id'))
    
    # Request details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100))  # plumbing, electrical, hvac, appliance, etc.
    priority = Column(Enum(MaintenancePriority), default=MaintenancePriority.MEDIUM)
    status = Column(Enum(MaintenanceStatus), default=MaintenanceStatus.PENDING)
    
    # Assignment and scheduling
    assigned_to = Column(String(200))  # Contractor/maintenance person
    contractor_contact = Column(String(100))
    scheduled_date = Column(DateTime)
    estimated_cost = Column(DECIMAL(10, 2))
    actual_cost = Column(DECIMAL(10, 2))
    
    # Timestamps
    reported_date = Column(DateTime, default=datetime.utcnow)
    started_date = Column(DateTime)
    completed_date = Column(DateTime)
    
    # Resolution
    resolution_notes = Column(Text)
    tenant_satisfaction = Column(Integer)  # 1-5 rating
    warranty_until = Column(DateTime)
    
    # Metadata
    photos = Column(Text)  # JSON array of photo URLs
    receipts = Column(Text)  # JSON array of receipt URLs
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    property = relationship("Property", back_populates="maintenance_requests")
    tenant = relationship("Tenant", back_populates="maintenance_requests")


class FinancialTransaction(Base):
    """Financial transaction tracking for properties"""
    __tablename__ = 'financial_transactions'

    id = Column(Integer, primary_key=True)
    transaction_number = Column(String(50), unique=True, nullable=False)
    property_id = Column(Integer, ForeignKey('properties.id'), nullable=False)
    
    # Transaction details
    transaction_type = Column(String(50), nullable=False)  # income, expense, repair, maintenance
    category = Column(String(100), nullable=False)  # rent, utilities, repair, insurance, etc.
    amount = Column(DECIMAL(12, 2), nullable=False)
    description = Column(String(500), nullable=False)
    
    # Payment information
    payment_method = Column(String(50))
    vendor = Column(String(200))
    invoice_number = Column(String(100))
    reference_number = Column(String(100))
    
    # Dates
    transaction_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime)
    paid_date = Column(DateTime)
    
    # Status and metadata
    is_recurring = Column(Boolean, default=False)
    recurring_frequency = Column(String(20))  # monthly, quarterly, yearly
    tax_deductible = Column(Boolean, default=False)
    notes = Column(Text)
    receipt_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    property = relationship("Property", back_populates="financial_transactions")


class PropertyDocument(Base):
    """Document storage for property-related files"""
    __tablename__ = 'property_documents'

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey('properties.id'))
    tenant_id = Column(Integer, ForeignKey('tenants.id'))
    lease_id = Column(Integer, ForeignKey('leases.id'))
    maintenance_request_id = Column(Integer, ForeignKey('maintenance_requests.id'))
    
    # Document details
    document_type = Column(String(100), nullable=False)  # lease, inspection, photo, receipt
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String(100))
    
    # Storage information
    storage_path = Column(String(500), nullable=False)
    document_id = Column(String(100))  # Reference to storage service
    
    # Metadata
    title = Column(String(200))
    description = Column(Text)
    tags = Column(Text)  # JSON array of tags
    is_confidential = Column(Boolean, default=False)
    uploaded_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
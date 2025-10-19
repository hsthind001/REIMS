"""
Enhanced REIMS Database Schema
Implements all missing tables from the implementation plan
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, DECIMAL, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from decimal import Decimal
import enum
import uuid

Base = declarative_base()

# Enums for better data integrity
class AlertLevel(enum.Enum):
    WARNING = "warning"
    CRITICAL = "critical"

class AlertStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class WorkflowLockStatus(enum.Enum):
    LOCKED = "locked"
    UNLOCKED = "unlocked"

class UserRole(enum.Enum):
    SUPERVISOR = "supervisor"
    ANALYST = "analyst"
    VIEWER = "viewer"

class StoreStatus(enum.Enum):
    OCCUPIED = "occupied"
    VACANT = "vacant"
    UNDER_LEASE = "under_lease"

# Enhanced Property Model (extends existing)
class EnhancedProperty(Base):
    """Enhanced property model with all required fields"""
    __tablename__ = 'enhanced_properties'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=False)
    total_sqft = Column(DECIMAL(12, 2))
    acquisition_cost = Column(DECIMAL(12, 2))
    current_value = Column(DECIMAL(12, 2))
    loan_balance = Column(DECIMAL(12, 2))
    interest_rate = Column(DECIMAL(5, 4))
    property_class = Column(String(50))  # Class A, B, C
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    stores = relationship("Store", back_populates="property", cascade="all, delete-orphan")
    financial_documents = relationship("FinancialDocument", back_populates="property", cascade="all, delete-orphan")
    property_costs = relationship("PropertyCost", back_populates="property", cascade="all, delete-orphan")
    alerts = relationship("CommitteeAlert", back_populates="property", cascade="all, delete-orphan")
    workflow_locks = relationship("WorkflowLock", back_populates="property", cascade="all, delete-orphan")

# Stores/Units Management
class Store(Base):
    """Store/unit tracking for properties"""
    __tablename__ = 'stores'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey('enhanced_properties.id'), nullable=False)
    unit_number = Column(String(50), nullable=False)
    sqft = Column(DECIMAL(10, 2), nullable=False)
    status = Column(Enum(StoreStatus), default=StoreStatus.VACANT)
    tenant_name = Column(String(255))
    lease_start = Column(DateTime)
    lease_end = Column(DateTime)
    monthly_rent = Column(DECIMAL(10, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    property = relationship("EnhancedProperty", back_populates="stores")

# Financial Documents
class FinancialDocument(Base):
    """Financial document management"""
    __tablename__ = 'financial_documents'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey('enhanced_properties.id'), nullable=False)
    file_path = Column(Text, nullable=False)
    document_type = Column(String(50), nullable=False)  # lease, offering_memorandum, financial_statement
    upload_date = Column(DateTime, default=datetime.utcnow)
    processing_status = Column(String(50), default="pending")
    
    # Relationships
    property = relationship("EnhancedProperty", back_populates="financial_documents")
    extracted_metrics = relationship("ExtractedMetric", back_populates="document", cascade="all, delete-orphan")

# Extracted Metrics
class ExtractedMetric(Base):
    """Extracted financial metrics from documents"""
    __tablename__ = 'extracted_metrics'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey('financial_documents.id'), nullable=False)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(DECIMAL(15, 2), nullable=False)
    confidence_score = Column(DECIMAL(3, 2), nullable=False)  # 0.00 to 1.00
    extraction_method = Column(String(50), nullable=False)  # table_structured, ocr_clear, pattern_match, ml_inference
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("FinancialDocument", back_populates="extracted_metrics")

# Property Costs
class PropertyCost(Base):
    """Property cost tracking"""
    __tablename__ = 'property_costs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey('enhanced_properties.id'), nullable=False)
    cost_type = Column(String(50), nullable=False)  # insurance, mortgage, utility, maintenance
    amount = Column(DECIMAL(12, 2), nullable=False)
    frequency = Column(String(20), nullable=False)  # monthly, annual, one-time
    date = Column(DateTime, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    property = relationship("EnhancedProperty", back_populates="property_costs")

# Committee Alerts System
class CommitteeAlert(Base):
    """Committee alert management system"""
    __tablename__ = 'committee_alerts'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey('enhanced_properties.id'), nullable=False)
    metric = Column(String(50), nullable=False)  # dscr, occupancy, revenue, etc.
    value = Column(DECIMAL(15, 4), nullable=False)
    threshold = Column(DECIMAL(15, 4), nullable=False)
    level = Column(Enum(AlertLevel), nullable=False)
    committee = Column(String(100), nullable=False)  # Finance Sub-Committee, Occupancy Sub-Committee
    status = Column(Enum(AlertStatus), default=AlertStatus.PENDING)
    approved_by = Column(UUID(as_uuid=True), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    property = relationship("EnhancedProperty", back_populates="alerts")
    workflow_locks = relationship("WorkflowLock", back_populates="alert", cascade="all, delete-orphan")

# Workflow Locks
class WorkflowLock(Base):
    """Workflow lock management"""
    __tablename__ = 'workflow_locks'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey('enhanced_properties.id'), nullable=False)
    alert_id = Column(UUID(as_uuid=True), ForeignKey('committee_alerts.id'), nullable=False)
    status = Column(Enum(WorkflowLockStatus), default=WorkflowLockStatus.LOCKED)
    locked_at = Column(DateTime, default=datetime.utcnow)
    unlocked_at = Column(DateTime, nullable=True)
    unlocked_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    property = relationship("EnhancedProperty", back_populates="workflow_locks")
    alert = relationship("CommitteeAlert", back_populates="workflow_locks")

# User Management
class User(Base):
    """User management for authentication"""
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.VIEWER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")

# Audit Logging
class AuditLog(Base):
    """Comprehensive audit logging system"""
    __tablename__ = 'audit_log'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    action = Column(String(100), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    br_id = Column(String(20), nullable=True)  # Business Requirement ID
    property_id = Column(UUID(as_uuid=True), nullable=True)
    document_id = Column(UUID(as_uuid=True), nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    timestamp = Column(DateTime, default=datetime.utcnow)
    session_id = Column(String(100), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")

# Anomaly Detection
class Anomaly(Base):
    """Anomaly detection results"""
    __tablename__ = 'anomalies'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey('enhanced_properties.id'), nullable=False)
    metric_name = Column(String(100), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    value = Column(DECIMAL(15, 4), nullable=False)
    z_score = Column(DECIMAL(8, 4), nullable=True)
    cusum_value = Column(DECIMAL(8, 4), nullable=True)
    detection_method = Column(String(50), nullable=False)  # z-score, cusum
    confidence = Column(DECIMAL(3, 2), nullable=False)
    trend_direction = Column(String(20), nullable=True)  # upward, downward
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    property = relationship("EnhancedProperty")

# Market Intelligence
class MarketAnalysis(Base):
    """Market intelligence analysis results"""
    __tablename__ = 'market_analysis'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey('enhanced_properties.id'), nullable=False)
    analysis_type = Column(String(50), nullable=False)  # location, demographics, tenant_recommendations
    analysis_data = Column(JSON, nullable=False)
    confidence_score = Column(DECIMAL(3, 2), nullable=False)
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    property = relationship("EnhancedProperty")

# Exit Strategy Analysis
class ExitStrategyAnalysis(Base):
    """Exit strategy analysis results"""
    __tablename__ = 'exit_strategy_analysis'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey('enhanced_properties.id'), nullable=False)
    recommended_strategy = Column(String(20), nullable=False)  # hold, refinance, sale
    confidence = Column(DECIMAL(3, 2), nullable=False)
    scenarios = Column(JSON, nullable=False)  # hold, refinance, sale scenarios
    rationale = Column(Text, nullable=False)
    analysis_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    property = relationship("EnhancedProperty")

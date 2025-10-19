-- ============================================================================
-- REIMS Stores Table Migration
-- Version: 002
-- Description: Create stores table for individual units/tenants within properties
-- Author: REIMS Development Team
-- Date: October 12, 2025
-- ============================================================================

-- Drop table if exists (for development/testing)
-- Uncomment next line if you want to recreate the table
-- DROP TABLE IF EXISTS stores CASCADE;

-- ============================================================================
-- Main Stores Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS stores (
  -- Primary Key
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Foreign Key to Properties
  property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
  
  -- ========================================================================
  -- Unit Identification
  -- ========================================================================
  unit_number VARCHAR(50) NOT NULL, -- "Suite 101", "Space A", etc.
  unit_name VARCHAR(255),
  
  -- ========================================================================
  -- Physical Characteristics
  -- ========================================================================
  sqft DECIMAL(10, 2) NOT NULL,
  floor_number INTEGER,
  
  -- ========================================================================
  -- Lease Information
  -- ========================================================================
  tenant_name VARCHAR(255),
  tenant_type VARCHAR(50), -- 'retail', 'office', 'restaurant', etc.
  
  -- ========================================================================
  -- Lease Dates
  -- ========================================================================
  lease_start_date DATE,
  lease_end_date DATE,
  lease_status VARCHAR(20) DEFAULT 'active', -- 'active', 'expired', 'pending', 'terminated'
  
  -- ========================================================================
  -- Financial Terms
  -- ========================================================================
  monthly_rent DECIMAL(12, 2),
  annual_rent DECIMAL(15, 2),
  rent_escalation_pct DECIMAL(5, 2), -- Annual escalation %
  security_deposit DECIMAL(12, 2),
  
  -- ========================================================================
  -- Current Status
  -- ========================================================================
  status VARCHAR(20) NOT NULL DEFAULT 'vacant', -- 'occupied', 'vacant', 'under_lease', 'maintenance'
  occupancy_date DATE,
  vacancy_date DATE,
  
  -- ========================================================================
  -- Additional Terms
  -- ========================================================================
  parking_spaces INTEGER DEFAULT 0,
  utilities_included BOOLEAN DEFAULT false,
  common_area_maintenance_fee DECIMAL(10, 2),
  
  -- ========================================================================
  -- Renewal Options
  -- ========================================================================
  renewal_option BOOLEAN DEFAULT false,
  renewal_term_months INTEGER,
  
  -- ========================================================================
  -- Contact Information
  -- ========================================================================
  tenant_contact_name VARCHAR(255),
  tenant_contact_phone VARCHAR(20),
  tenant_contact_email VARCHAR(255),
  
  -- ========================================================================
  -- Audit Trail
  -- ========================================================================
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_by UUID,
  updated_by UUID,
  
  -- ========================================================================
  -- Unique Constraint
  -- ========================================================================
  CONSTRAINT uq_stores_property_unit UNIQUE (property_id, unit_number)
);

-- ============================================================================
-- Performance Indexes
-- ============================================================================

-- Property ID index (for filtering units by property)
CREATE INDEX IF NOT EXISTS idx_stores_property_id 
  ON stores(property_id);

-- Status index (for filtering by occupancy status)
CREATE INDEX IF NOT EXISTS idx_stores_status 
  ON stores(status);

-- Composite index for property + status queries
CREATE INDEX IF NOT EXISTS idx_stores_property_status 
  ON stores(property_id, status);

-- Lease end date index (for vacancy forecasting)
CREATE INDEX IF NOT EXISTS idx_stores_lease_end_date 
  ON stores(lease_end_date) 
  WHERE lease_end_date IS NOT NULL;

-- Tenant name index (for searching tenants)
CREATE INDEX IF NOT EXISTS idx_stores_tenant_name 
  ON stores(tenant_name) 
  WHERE tenant_name IS NOT NULL;

-- Created date index (for sorting by newest)
CREATE INDEX IF NOT EXISTS idx_stores_created_at 
  ON stores(created_at DESC);

-- Lease status index (for filtering active leases)
CREATE INDEX IF NOT EXISTS idx_stores_lease_status 
  ON stores(lease_status);

-- Tenant type index (for filtering by business type)
CREATE INDEX IF NOT EXISTS idx_stores_tenant_type 
  ON stores(tenant_type) 
  WHERE tenant_type IS NOT NULL;

-- Unit number index (for quick lookups)
CREATE INDEX IF NOT EXISTS idx_stores_unit_number 
  ON stores(unit_number);

-- ============================================================================
-- Constraints
-- ============================================================================

-- Square footage must be positive
ALTER TABLE stores 
  DROP CONSTRAINT IF EXISTS chk_sqft_positive;
ALTER TABLE stores 
  ADD CONSTRAINT chk_sqft_positive 
  CHECK (sqft > 0);

-- Monthly rent must be non-negative
ALTER TABLE stores 
  DROP CONSTRAINT IF EXISTS chk_rent_positive;
ALTER TABLE stores 
  ADD CONSTRAINT chk_rent_positive 
  CHECK (monthly_rent IS NULL OR monthly_rent >= 0);

-- Lease end date must be after start date
ALTER TABLE stores 
  DROP CONSTRAINT IF EXISTS chk_lease_dates;
ALTER TABLE stores 
  ADD CONSTRAINT chk_lease_dates 
  CHECK (lease_start_date IS NULL OR lease_end_date IS NULL 
    OR lease_end_date >= lease_start_date);

-- Status must be valid
ALTER TABLE stores 
  DROP CONSTRAINT IF EXISTS chk_valid_status;
ALTER TABLE stores 
  ADD CONSTRAINT chk_valid_status 
  CHECK (status IN ('occupied', 'vacant', 'under_lease', 'maintenance'));

-- Lease status must be valid
ALTER TABLE stores 
  DROP CONSTRAINT IF EXISTS chk_valid_lease_status;
ALTER TABLE stores 
  ADD CONSTRAINT chk_valid_lease_status 
  CHECK (lease_status IN ('active', 'expired', 'pending', 'terminated', 'month_to_month'));

-- Tenant type must be valid
ALTER TABLE stores 
  DROP CONSTRAINT IF EXISTS chk_valid_tenant_type;
ALTER TABLE stores 
  ADD CONSTRAINT chk_valid_tenant_type 
  CHECK (tenant_type IS NULL OR tenant_type IN (
    'retail', 'office', 'restaurant', 'medical', 'fitness', 
    'salon', 'warehouse', 'mixed_use', 'other'
  ));

-- Parking spaces must be non-negative
ALTER TABLE stores 
  DROP CONSTRAINT IF EXISTS chk_parking_non_negative;
ALTER TABLE stores 
  ADD CONSTRAINT chk_parking_non_negative 
  CHECK (parking_spaces >= 0);

-- Annual rent should match monthly rent * 12 (if both present)
ALTER TABLE stores 
  DROP CONSTRAINT IF EXISTS chk_annual_rent_consistency;
ALTER TABLE stores 
  ADD CONSTRAINT chk_annual_rent_consistency 
  CHECK (
    monthly_rent IS NULL OR annual_rent IS NULL OR 
    ABS(annual_rent - (monthly_rent * 12)) < 1.0
  );

-- Occupancy date should not be in the future
ALTER TABLE stores 
  DROP CONSTRAINT IF EXISTS chk_occupancy_date_valid;
ALTER TABLE stores 
  ADD CONSTRAINT chk_occupancy_date_valid 
  CHECK (occupancy_date IS NULL OR occupancy_date <= CURRENT_DATE);

-- Vacancy date should not be before occupancy date
ALTER TABLE stores 
  DROP CONSTRAINT IF EXISTS chk_vacancy_after_occupancy;
ALTER TABLE stores 
  ADD CONSTRAINT chk_vacancy_after_occupancy 
  CHECK (
    occupancy_date IS NULL OR vacancy_date IS NULL OR 
    vacancy_date >= occupancy_date
  );

-- ============================================================================
-- Trigger for Updated Timestamp
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_stores_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop trigger if exists
DROP TRIGGER IF EXISTS trg_stores_updated_at ON stores;

-- Create trigger
CREATE TRIGGER trg_stores_updated_at
  BEFORE UPDATE ON stores
  FOR EACH ROW
  EXECUTE FUNCTION update_stores_updated_at();

-- ============================================================================
-- Function to Calculate Property Occupancy
-- ============================================================================

CREATE OR REPLACE FUNCTION calculate_property_occupancy(p_property_id UUID)
RETURNS DECIMAL(5, 2) AS $$
DECLARE
  occupied_count INTEGER;
  total_count INTEGER;
  occupancy_rate DECIMAL(5, 2);
BEGIN
  -- Count occupied units
  SELECT COUNT(*) INTO occupied_count
  FROM stores
  WHERE property_id = p_property_id 
    AND status = 'occupied';
  
  -- Count total units
  SELECT COUNT(*) INTO total_count
  FROM stores
  WHERE property_id = p_property_id;
  
  -- Calculate occupancy rate
  IF total_count = 0 THEN
    RETURN 0;
  ELSE
    occupancy_rate := (occupied_count::DECIMAL / total_count::DECIMAL) * 100;
    RETURN ROUND(occupancy_rate, 2);
  END IF;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Function to Update Property Occupancy (Auto-sync)
-- ============================================================================

CREATE OR REPLACE FUNCTION sync_property_occupancy()
RETURNS TRIGGER AS $$
DECLARE
  new_occupancy_rate DECIMAL(5, 2);
  occupied_count INTEGER;
  total_count INTEGER;
BEGIN
  -- Get property_id (from NEW or OLD record)
  DECLARE
    p_id UUID;
  BEGIN
    p_id := COALESCE(NEW.property_id, OLD.property_id);
    
    -- Calculate new occupancy
    SELECT 
      COUNT(*) FILTER (WHERE status = 'occupied'),
      COUNT(*)
    INTO occupied_count, total_count
    FROM stores
    WHERE property_id = p_id;
    
    -- Calculate rate
    IF total_count > 0 THEN
      new_occupancy_rate := (occupied_count::DECIMAL / total_count::DECIMAL) * 100;
    ELSE
      new_occupancy_rate := 0;
    END IF;
    
    -- Update properties table
    UPDATE properties
    SET 
      occupied_units = occupied_count,
      total_units = total_count,
      occupancy_rate = ROUND(new_occupancy_rate, 2)
    WHERE id = p_id;
  END;
  
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Drop trigger if exists
DROP TRIGGER IF EXISTS trg_sync_property_occupancy ON stores;

-- Create trigger to auto-sync property occupancy
CREATE TRIGGER trg_sync_property_occupancy
  AFTER INSERT OR UPDATE OR DELETE ON stores
  FOR EACH ROW
  EXECUTE FUNCTION sync_property_occupancy();

-- ============================================================================
-- Comments for Documentation
-- ============================================================================

COMMENT ON TABLE stores IS 'Individual units/spaces within properties (stores, offices, suites)';

COMMENT ON COLUMN stores.id IS 'Unique identifier (UUID) for the store/unit';
COMMENT ON COLUMN stores.property_id IS 'Foreign key to properties table';
COMMENT ON COLUMN stores.unit_number IS 'Unit identifier within property (e.g., "Suite 101", "Space A")';
COMMENT ON COLUMN stores.unit_name IS 'Optional descriptive name for the unit';
COMMENT ON COLUMN stores.sqft IS 'Square footage of the unit';
COMMENT ON COLUMN stores.floor_number IS 'Floor number (1 = ground floor)';
COMMENT ON COLUMN stores.tenant_name IS 'Current tenant business name';
COMMENT ON COLUMN stores.tenant_type IS 'Type: retail, office, restaurant, medical, fitness, salon, warehouse, mixed_use, other';
COMMENT ON COLUMN stores.lease_start_date IS 'Date when lease begins';
COMMENT ON COLUMN stores.lease_end_date IS 'Date when lease expires (critical for vacancy forecasting)';
COMMENT ON COLUMN stores.lease_status IS 'Lease status: active, expired, pending, terminated, month_to_month';
COMMENT ON COLUMN stores.monthly_rent IS 'Monthly rent payment';
COMMENT ON COLUMN stores.annual_rent IS 'Annual rent (should equal monthly_rent * 12)';
COMMENT ON COLUMN stores.rent_escalation_pct IS 'Annual rent escalation percentage';
COMMENT ON COLUMN stores.security_deposit IS 'Security deposit amount';
COMMENT ON COLUMN stores.status IS 'Current status: occupied, vacant, under_lease, maintenance';
COMMENT ON COLUMN stores.occupancy_date IS 'Date when unit became occupied';
COMMENT ON COLUMN stores.vacancy_date IS 'Date when unit became vacant';
COMMENT ON COLUMN stores.parking_spaces IS 'Number of parking spaces allocated';
COMMENT ON COLUMN stores.utilities_included IS 'Whether utilities are included in rent';
COMMENT ON COLUMN stores.common_area_maintenance_fee IS 'CAM fee (Common Area Maintenance)';
COMMENT ON COLUMN stores.renewal_option IS 'Whether tenant has renewal option';
COMMENT ON COLUMN stores.renewal_term_months IS 'Length of renewal term in months';
COMMENT ON COLUMN stores.tenant_contact_name IS 'Primary tenant contact person';
COMMENT ON COLUMN stores.tenant_contact_phone IS 'Tenant contact phone number';
COMMENT ON COLUMN stores.tenant_contact_email IS 'Tenant contact email';
COMMENT ON COLUMN stores.created_at IS 'Timestamp when record was created';
COMMENT ON COLUMN stores.updated_at IS 'Timestamp when record was last updated';
COMMENT ON COLUMN stores.created_by IS 'UUID of user who created the record';
COMMENT ON COLUMN stores.updated_by IS 'UUID of user who last updated the record';

-- ============================================================================
-- Success Message
-- ============================================================================

DO $$
BEGIN
  RAISE NOTICE '✅ Stores table created successfully';
  RAISE NOTICE '✅ Indexes created (9 indexes)';
  RAISE NOTICE '✅ Constraints added (10 constraints)';
  RAISE NOTICE '✅ Triggers created (updated_at, sync_property_occupancy)';
  RAISE NOTICE '✅ Functions created (calculate_property_occupancy, sync_property_occupancy)';
  RAISE NOTICE '✅ Comments added for documentation';
  RAISE NOTICE '';
  RAISE NOTICE '📊 Table: stores';
  RAISE NOTICE '📊 Columns: 32';
  RAISE NOTICE '📊 Indexes: 9';
  RAISE NOTICE '📊 Constraints: 10';
  RAISE NOTICE '📊 Triggers: 2';
  RAISE NOTICE '📊 Functions: 2';
  RAISE NOTICE '';
  RAISE NOTICE '🔗 Foreign Key: property_id → properties(id) ON DELETE CASCADE';
  RAISE NOTICE '🔗 Unique: (property_id, unit_number)';
  RAISE NOTICE '';
  RAISE NOTICE '⚡ Auto-Sync: Property occupancy_rate updates automatically!';
  RAISE NOTICE '';
  RAISE NOTICE '🔍 Sample query:';
  RAISE NOTICE '   SELECT unit_number, tenant_name, status, monthly_rent';
  RAISE NOTICE '   FROM stores WHERE property_id = ''your-property-id'' ORDER BY unit_number;';
  RAISE NOTICE '';
  RAISE NOTICE '🔍 Calculate occupancy:';
  RAISE NOTICE '   SELECT calculate_property_occupancy(''your-property-id'');';
END $$;

















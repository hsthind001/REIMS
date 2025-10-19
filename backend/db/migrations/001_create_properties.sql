-- ============================================================================
-- REIMS Properties Table Migration
-- Version: 001
-- Description: Create properties table with comprehensive real estate data
-- Author: REIMS Development Team
-- Date: October 12, 2025
-- ============================================================================

-- Drop table if exists (for development/testing)
-- Uncomment next line if you want to recreate the table
-- DROP TABLE IF EXISTS properties CASCADE;

-- ============================================================================
-- Main Properties Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS properties (
  -- Primary Key
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- ========================================================================
  -- Basic Information
  -- ========================================================================
  name VARCHAR(255) NOT NULL,
  description TEXT,
  
  -- ========================================================================
  -- Location Information
  -- ========================================================================
  address TEXT NOT NULL,
  city VARCHAR(100) NOT NULL,
  state VARCHAR(50) NOT NULL,
  zip_code VARCHAR(20),
  latitude DECIMAL(10, 8),
  longitude DECIMAL(11, 8),
  
  -- ========================================================================
  -- Physical Characteristics
  -- ========================================================================
  total_sqft DECIMAL(12, 2),
  year_built INTEGER,
  property_type VARCHAR(50), -- 'office', 'retail', 'mixed-use', 'industrial'
  property_class VARCHAR(20), -- 'A', 'B', 'C'
  
  -- ========================================================================
  -- Financial Information - Acquisition
  -- ========================================================================
  acquisition_cost DECIMAL(15, 2),
  acquisition_date DATE,
  
  -- ========================================================================
  -- Financial Information - Current Valuation
  -- ========================================================================
  current_value DECIMAL(15, 2),
  last_appraised_date DATE,
  estimated_market_value DECIMAL(15, 2),
  
  -- ========================================================================
  -- Debt Information
  -- ========================================================================
  loan_balance DECIMAL(15, 2),
  original_loan_amount DECIMAL(15, 2),
  interest_rate DECIMAL(5, 3), -- e.g., 5.250% = 5.250
  loan_maturity_date DATE,
  dscr DECIMAL(4, 2), -- Debt Service Coverage Ratio (e.g., 1.25)
  
  -- ========================================================================
  -- Income Information
  -- ========================================================================
  annual_noi DECIMAL(15, 2), -- Net Operating Income
  annual_revenue DECIMAL(15, 2),
  
  -- ========================================================================
  -- Occupancy Information
  -- ========================================================================
  total_units INTEGER,
  occupied_units INTEGER,
  occupancy_rate DECIMAL(5, 2), -- 0.00 to 100.00 (percentage)
  
  -- ========================================================================
  -- Status and Flags
  -- ========================================================================
  status VARCHAR(20) DEFAULT 'active', -- 'active', 'sold', 'under_renovation'
  has_active_alerts BOOLEAN DEFAULT false,
  
  -- ========================================================================
  -- Audit Trail
  -- ========================================================================
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_by UUID,
  updated_by UUID
);

-- ============================================================================
-- Performance Indexes
-- ============================================================================

-- Status index (for filtering active properties)
CREATE INDEX IF NOT EXISTS idx_properties_status 
  ON properties(status);

-- Location index (for geographic queries)
CREATE INDEX IF NOT EXISTS idx_properties_city_state 
  ON properties(city, state);

-- Property type index (for filtering by type)
CREATE INDEX IF NOT EXISTS idx_properties_property_type 
  ON properties(property_type);

-- Occupancy rate index (for performance queries)
CREATE INDEX IF NOT EXISTS idx_properties_occupancy_rate 
  ON properties(occupancy_rate DESC);

-- Created date index (for sorting by newest)
CREATE INDEX IF NOT EXISTS idx_properties_created_at 
  ON properties(created_at DESC);

-- Alert flag index (for quick alert filtering)
CREATE INDEX IF NOT EXISTS idx_properties_has_alerts 
  ON properties(has_active_alerts) 
  WHERE has_active_alerts = true;

-- Current value index (for portfolio valuation queries)
CREATE INDEX IF NOT EXISTS idx_properties_current_value 
  ON properties(current_value DESC);

-- Geographic coordinate index (for map-based queries)
CREATE INDEX IF NOT EXISTS idx_properties_coordinates 
  ON properties(latitude, longitude) 
  WHERE latitude IS NOT NULL AND longitude IS NOT NULL;

-- Property class index (for filtering by class)
CREATE INDEX IF NOT EXISTS idx_properties_class 
  ON properties(property_class);

-- ============================================================================
-- Constraints
-- ============================================================================

-- Occupancy rate must be between 0 and 100
ALTER TABLE properties 
  DROP CONSTRAINT IF EXISTS chk_occupancy_rate;
ALTER TABLE properties 
  ADD CONSTRAINT chk_occupancy_rate 
  CHECK (occupancy_rate IS NULL OR (occupancy_rate >= 0 AND occupancy_rate <= 100));

-- Total square footage must be positive
ALTER TABLE properties 
  DROP CONSTRAINT IF EXISTS chk_sqft_positive;
ALTER TABLE properties 
  ADD CONSTRAINT chk_sqft_positive 
  CHECK (total_sqft IS NULL OR total_sqft > 0);

-- Acquisition date cannot be in the future
ALTER TABLE properties 
  DROP CONSTRAINT IF EXISTS chk_acquisition_before_current;
ALTER TABLE properties 
  ADD CONSTRAINT chk_acquisition_before_current 
  CHECK (acquisition_date IS NULL OR acquisition_date <= CURRENT_DATE);

-- Year built must be reasonable
ALTER TABLE properties 
  DROP CONSTRAINT IF EXISTS chk_year_built_reasonable;
ALTER TABLE properties 
  ADD CONSTRAINT chk_year_built_reasonable 
  CHECK (year_built IS NULL OR (year_built >= 1800 AND year_built <= EXTRACT(YEAR FROM CURRENT_DATE) + 5));

-- Occupied units cannot exceed total units
ALTER TABLE properties 
  DROP CONSTRAINT IF EXISTS chk_occupied_within_total;
ALTER TABLE properties 
  ADD CONSTRAINT chk_occupied_within_total 
  CHECK (occupied_units IS NULL OR total_units IS NULL OR occupied_units <= total_units);

-- Status must be valid
ALTER TABLE properties 
  DROP CONSTRAINT IF EXISTS chk_valid_status;
ALTER TABLE properties 
  ADD CONSTRAINT chk_valid_status 
  CHECK (status IN ('active', 'sold', 'under_renovation', 'pending_sale', 'inactive'));

-- Property type must be valid
ALTER TABLE properties 
  DROP CONSTRAINT IF EXISTS chk_valid_property_type;
ALTER TABLE properties 
  ADD CONSTRAINT chk_valid_property_type 
  CHECK (property_type IS NULL OR property_type IN ('office', 'retail', 'mixed-use', 'industrial', 'residential', 'warehouse'));

-- Property class must be valid
ALTER TABLE properties 
  DROP CONSTRAINT IF EXISTS chk_valid_property_class;
ALTER TABLE properties 
  ADD CONSTRAINT chk_valid_property_class 
  CHECK (property_class IS NULL OR property_class IN ('A', 'B', 'C', 'D'));

-- ============================================================================
-- Trigger for Updated Timestamp
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_properties_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop trigger if exists
DROP TRIGGER IF EXISTS trg_properties_updated_at ON properties;

-- Create trigger
CREATE TRIGGER trg_properties_updated_at
  BEFORE UPDATE ON properties
  FOR EACH ROW
  EXECUTE FUNCTION update_properties_updated_at();

-- ============================================================================
-- Comments for Documentation
-- ============================================================================

COMMENT ON TABLE properties IS 'Core table storing all real estate property information for portfolio management';

COMMENT ON COLUMN properties.id IS 'Unique identifier (UUID) for the property';
COMMENT ON COLUMN properties.name IS 'Property name (e.g., "Downtown Office Commons")';
COMMENT ON COLUMN properties.description IS 'Detailed description of the property';
COMMENT ON COLUMN properties.address IS 'Full street address';
COMMENT ON COLUMN properties.city IS 'City name';
COMMENT ON COLUMN properties.state IS 'State or province';
COMMENT ON COLUMN properties.zip_code IS 'Postal/ZIP code';
COMMENT ON COLUMN properties.latitude IS 'Geographic latitude (WGS84)';
COMMENT ON COLUMN properties.longitude IS 'Geographic longitude (WGS84)';
COMMENT ON COLUMN properties.total_sqft IS 'Total square footage of property';
COMMENT ON COLUMN properties.year_built IS 'Year the property was constructed';
COMMENT ON COLUMN properties.property_type IS 'Type: office, retail, mixed-use, industrial, residential, warehouse';
COMMENT ON COLUMN properties.property_class IS 'Class A (prime), B (good), C (fair), D (below average)';
COMMENT ON COLUMN properties.acquisition_cost IS 'Original purchase price';
COMMENT ON COLUMN properties.acquisition_date IS 'Date property was acquired';
COMMENT ON COLUMN properties.current_value IS 'Current estimated value (used for portfolio calculations)';
COMMENT ON COLUMN properties.last_appraised_date IS 'Date of most recent appraisal';
COMMENT ON COLUMN properties.estimated_market_value IS 'Estimated market value from appraisal';
COMMENT ON COLUMN properties.loan_balance IS 'Remaining loan amount';
COMMENT ON COLUMN properties.original_loan_amount IS 'Original loan principal';
COMMENT ON COLUMN properties.interest_rate IS 'Loan interest rate (percentage)';
COMMENT ON COLUMN properties.loan_maturity_date IS 'Date when loan matures';
COMMENT ON COLUMN properties.dscr IS 'Debt Service Coverage Ratio (Annual NOI / Annual Debt Service)';
COMMENT ON COLUMN properties.annual_noi IS 'Annual Net Operating Income';
COMMENT ON COLUMN properties.annual_revenue IS 'Annual gross revenue';
COMMENT ON COLUMN properties.total_units IS 'Total number of units/spaces';
COMMENT ON COLUMN properties.occupied_units IS 'Number of currently occupied units';
COMMENT ON COLUMN properties.occupancy_rate IS 'Occupancy percentage (0-100)';
COMMENT ON COLUMN properties.status IS 'Current status: active, sold, under_renovation, pending_sale, inactive';
COMMENT ON COLUMN properties.has_active_alerts IS 'Flag indicating if property has active alerts';
COMMENT ON COLUMN properties.created_at IS 'Timestamp when record was created';
COMMENT ON COLUMN properties.updated_at IS 'Timestamp when record was last updated';
COMMENT ON COLUMN properties.created_by IS 'UUID of user who created the record';
COMMENT ON COLUMN properties.updated_by IS 'UUID of user who last updated the record';

-- ============================================================================
-- Success Message
-- ============================================================================

DO $$
BEGIN
  RAISE NOTICE '✅ Properties table created successfully';
  RAISE NOTICE '✅ Indexes created (9 indexes)';
  RAISE NOTICE '✅ Constraints added (8 constraints)';
  RAISE NOTICE '✅ Triggers created (updated_at trigger)';
  RAISE NOTICE '✅ Comments added for documentation';
  RAISE NOTICE '';
  RAISE NOTICE '📊 Table: properties';
  RAISE NOTICE '📊 Columns: 38';
  RAISE NOTICE '📊 Indexes: 9';
  RAISE NOTICE '📊 Constraints: 8';
  RAISE NOTICE '';
  RAISE NOTICE '🔍 Sample query:';
  RAISE NOTICE '   SELECT name, city, state, occupancy_rate, current_value FROM properties WHERE status = ''active'';';
END $$;

















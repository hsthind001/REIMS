-- Migration 010: Create Property Financial Summary Table
-- Purpose: Denormalized financial summary for fast dashboard queries
-- Required by: Dashboard KPI calculations, performance optimization
-- Date: 2025-10-12

-- ============================================================================
-- PROPERTY_FINANCIAL_SUMMARY TABLE: Pre-calculated metrics for performance
-- ============================================================================

CREATE TABLE IF NOT EXISTS property_financial_summary (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
  
  -- Summary Period
  summary_date DATE NOT NULL,
  summary_month VARCHAR(7), -- '2025-10' format (YYYY-MM)
  
  -- Income Metrics
  gross_revenue DECIMAL(15, 2),
  total_expenses DECIMAL(15, 2),
  noi DECIMAL(15, 2), -- Net Operating Income
  noi_margin DECIMAL(5, 3), -- NOI / Gross Revenue (e.g., 0.350 = 35%)
  
  -- Debt Metrics
  annual_debt_service DECIMAL(15, 2),
  dscr DECIMAL(4, 2), -- Debt Service Coverage Ratio
  ltv DECIMAL(3, 2), -- Loan-to-Value ratio (e.g., 0.75 = 75%)
  
  -- Occupancy Metrics
  total_units INTEGER,
  occupied_units INTEGER,
  occupancy_rate DECIMAL(3, 2), -- e.g., 0.92 = 92%
  leased_not_occupied INTEGER, -- Leased but tenant hasn't moved in yet
  vacant_units INTEGER,
  
  -- Tenant Metrics
  tenant_count INTEGER,
  average_lease_term_months DECIMAL(5, 1),
  expiring_leases_12mo INTEGER, -- Leases expiring in next 12 months
  
  -- Performance Metrics
  cap_rate DECIMAL(5, 3), -- Capitalization Rate: NOI / Property Value
  roi_pct DECIMAL(5, 2), -- Return on investment percentage
  days_on_market INTEGER,
  
  -- Area/Expense Breakdown
  expense_per_sqft DECIMAL(10, 2),
  revenue_per_sqft DECIMAL(10, 2),
  rent_per_occupied_sqft DECIMAL(10, 2),
  
  -- Quality Indicators
  avg_rent_per_unit DECIMAL(12, 2),
  rent_growth_pct_yoy DECIMAL(5, 2), -- Year-over-year growth percentage
  expense_ratio DECIMAL(5, 3), -- Expenses / Revenue
  
  -- Flag Indicators (Risk Detection)
  below_market_rent BOOLEAN DEFAULT false,
  above_average_expense BOOLEAN DEFAULT false,
  lease_expiration_risk BOOLEAN DEFAULT false,
  
  -- Audit
  calculated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  data_complete BOOLEAN DEFAULT true
);

-- ============================================================================
-- INDEXES: Optimized for dashboard queries
-- ============================================================================

-- Property-specific summaries
CREATE INDEX idx_summary_property_id ON property_financial_summary(property_id);

-- Temporal queries (most recent first)
CREATE INDEX idx_summary_date ON property_financial_summary(summary_date DESC);

-- Month-based queries
CREATE INDEX idx_summary_month ON property_financial_summary(summary_month DESC);

-- Risk flags for alerts
CREATE INDEX idx_summary_below_market ON property_financial_summary(below_market_rent) 
  WHERE below_market_rent = true;

CREATE INDEX idx_summary_high_expense ON property_financial_summary(above_average_expense) 
  WHERE above_average_expense = true;

CREATE INDEX idx_summary_lease_risk ON property_financial_summary(lease_expiration_risk) 
  WHERE lease_expiration_risk = true;

-- Performance queries
CREATE INDEX idx_summary_occupancy ON property_financial_summary(occupancy_rate DESC);
CREATE INDEX idx_summary_dscr ON property_financial_summary(dscr DESC);
CREATE INDEX idx_summary_noi ON property_financial_summary(noi DESC);

-- ============================================================================
-- CONSTRAINTS: Data validation and business rules
-- ============================================================================

-- Unique constraint: one record per property per month
ALTER TABLE property_financial_summary 
  ADD CONSTRAINT unique_property_month UNIQUE(property_id, summary_month);

-- Occupancy rate between 0 and 1 (0% to 100%)
ALTER TABLE property_financial_summary
  ADD CONSTRAINT chk_occupancy_rate 
  CHECK (occupancy_rate IS NULL OR (occupancy_rate >= 0.00 AND occupancy_rate <= 1.00));

-- NOI margin must be reasonable
ALTER TABLE property_financial_summary
  ADD CONSTRAINT chk_noi_margin 
  CHECK (noi_margin IS NULL OR (noi_margin >= -1.00 AND noi_margin <= 1.00));

-- DSCR must be positive
ALTER TABLE property_financial_summary
  ADD CONSTRAINT chk_dscr 
  CHECK (dscr IS NULL OR dscr >= 0.00);

-- LTV between 0 and 1 (0% to 100%)
ALTER TABLE property_financial_summary
  ADD CONSTRAINT chk_ltv 
  CHECK (ltv IS NULL OR (ltv >= 0.00 AND ltv <= 1.00));

-- Cap rate must be reasonable (-1.00 to 1.00)
ALTER TABLE property_financial_summary
  ADD CONSTRAINT chk_cap_rate 
  CHECK (cap_rate IS NULL OR (cap_rate >= -1.00 AND cap_rate <= 1.00));

-- ROI percentage must be reasonable
ALTER TABLE property_financial_summary
  ADD CONSTRAINT chk_roi_pct 
  CHECK (roi_pct IS NULL OR (roi_pct >= -100.00 AND roi_pct <= 1000.00));

-- Expense ratio between 0 and 1
ALTER TABLE property_financial_summary
  ADD CONSTRAINT chk_expense_ratio 
  CHECK (expense_ratio IS NULL OR (expense_ratio >= 0.00 AND expense_ratio <= 1.00));

-- Occupied units cannot exceed total units
ALTER TABLE property_financial_summary
  ADD CONSTRAINT chk_occupied_units 
  CHECK (occupied_units IS NULL OR total_units IS NULL OR occupied_units <= total_units);

-- Vacant units calculation check
ALTER TABLE property_financial_summary
  ADD CONSTRAINT chk_vacant_units 
  CHECK (vacant_units IS NULL OR vacant_units >= 0);

-- Days on market must be non-negative
ALTER TABLE property_financial_summary
  ADD CONSTRAINT chk_days_on_market 
  CHECK (days_on_market IS NULL OR days_on_market >= 0);

-- Tenant count must be non-negative
ALTER TABLE property_financial_summary
  ADD CONSTRAINT chk_tenant_count 
  CHECK (tenant_count IS NULL OR tenant_count >= 0);

-- Average lease term must be positive
ALTER TABLE property_financial_summary
  ADD CONSTRAINT chk_avg_lease_term 
  CHECK (average_lease_term_months IS NULL OR average_lease_term_months > 0);

-- Expiring leases must be non-negative
ALTER TABLE property_financial_summary
  ADD CONSTRAINT chk_expiring_leases 
  CHECK (expiring_leases_12mo IS NULL OR expiring_leases_12mo >= 0);

-- Per-square-foot metrics must be non-negative
ALTER TABLE property_financial_summary
  ADD CONSTRAINT chk_expense_per_sqft 
  CHECK (expense_per_sqft IS NULL OR expense_per_sqft >= 0);

ALTER TABLE property_financial_summary
  ADD CONSTRAINT chk_revenue_per_sqft 
  CHECK (revenue_per_sqft IS NULL OR revenue_per_sqft >= 0);

ALTER TABLE property_financial_summary
  ADD CONSTRAINT chk_rent_per_sqft 
  CHECK (rent_per_occupied_sqft IS NULL OR rent_per_occupied_sqft >= 0);

-- Summary month format validation (basic check)
ALTER TABLE property_financial_summary
  ADD CONSTRAINT chk_summary_month_format 
  CHECK (summary_month IS NULL OR summary_month ~ '^\d{4}-\d{2}$');

-- Summary date should not be in the future
ALTER TABLE property_financial_summary
  ADD CONSTRAINT chk_summary_date 
  CHECK (summary_date <= CURRENT_DATE);

-- ============================================================================
-- TRIGGERS: Auto-update summary_month from summary_date
-- ============================================================================

-- Function to auto-populate summary_month
CREATE OR REPLACE FUNCTION set_summary_month()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.summary_date IS NOT NULL THEN
    NEW.summary_month = TO_CHAR(NEW.summary_date, 'YYYY-MM');
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-set summary_month
CREATE TRIGGER trigger_set_summary_month
  BEFORE INSERT OR UPDATE OF summary_date ON property_financial_summary
  FOR EACH ROW
  EXECUTE FUNCTION set_summary_month();

-- ============================================================================
-- TABLE COMMENTS: Documentation for database administrators
-- ============================================================================

COMMENT ON TABLE property_financial_summary IS 'Denormalized financial summary for fast dashboard queries. Updated daily/monthly via batch job. Aggregates data from properties, stores, documents, and metrics tables. Pre-calculated to eliminate joins.';

COMMENT ON COLUMN property_financial_summary.property_id IS 'Property this summary belongs to';
COMMENT ON COLUMN property_financial_summary.summary_date IS 'Date of this summary snapshot';
COMMENT ON COLUMN property_financial_summary.summary_month IS 'Month in YYYY-MM format (auto-generated from summary_date)';

COMMENT ON COLUMN property_financial_summary.gross_revenue IS 'Total revenue for the period';
COMMENT ON COLUMN property_financial_summary.total_expenses IS 'Total expenses for the period';
COMMENT ON COLUMN property_financial_summary.noi IS 'Net Operating Income (gross_revenue - total_expenses)';
COMMENT ON COLUMN property_financial_summary.noi_margin IS 'NOI margin as decimal (NOI / gross_revenue)';

COMMENT ON COLUMN property_financial_summary.annual_debt_service IS 'Annual debt service amount';
COMMENT ON COLUMN property_financial_summary.dscr IS 'Debt Service Coverage Ratio (NOI / debt_service)';
COMMENT ON COLUMN property_financial_summary.ltv IS 'Loan-to-Value ratio as decimal (e.g., 0.75 = 75%)';

COMMENT ON COLUMN property_financial_summary.total_units IS 'Total rentable units';
COMMENT ON COLUMN property_financial_summary.occupied_units IS 'Currently occupied units';
COMMENT ON COLUMN property_financial_summary.occupancy_rate IS 'Occupancy rate as decimal (e.g., 0.92 = 92%)';
COMMENT ON COLUMN property_financial_summary.leased_not_occupied IS 'Units leased but not yet occupied';
COMMENT ON COLUMN property_financial_summary.vacant_units IS 'Vacant units available for lease';

COMMENT ON COLUMN property_financial_summary.tenant_count IS 'Total number of tenants';
COMMENT ON COLUMN property_financial_summary.average_lease_term_months IS 'Average lease term in months';
COMMENT ON COLUMN property_financial_summary.expiring_leases_12mo IS 'Number of leases expiring in next 12 months';

COMMENT ON COLUMN property_financial_summary.cap_rate IS 'Capitalization rate (NOI / property_value)';
COMMENT ON COLUMN property_financial_summary.roi_pct IS 'Return on investment as percentage';
COMMENT ON COLUMN property_financial_summary.days_on_market IS 'Days property has been on market';

COMMENT ON COLUMN property_financial_summary.expense_per_sqft IS 'Expenses per square foot';
COMMENT ON COLUMN property_financial_summary.revenue_per_sqft IS 'Revenue per square foot';
COMMENT ON COLUMN property_financial_summary.rent_per_occupied_sqft IS 'Rent per occupied square foot';

COMMENT ON COLUMN property_financial_summary.avg_rent_per_unit IS 'Average rent per unit';
COMMENT ON COLUMN property_financial_summary.rent_growth_pct_yoy IS 'Year-over-year rent growth percentage';
COMMENT ON COLUMN property_financial_summary.expense_ratio IS 'Expense ratio (expenses / revenue)';

COMMENT ON COLUMN property_financial_summary.below_market_rent IS 'Flag: rent is below market average';
COMMENT ON COLUMN property_financial_summary.above_average_expense IS 'Flag: expenses are above average';
COMMENT ON COLUMN property_financial_summary.lease_expiration_risk IS 'Flag: high lease expiration risk';

COMMENT ON COLUMN property_financial_summary.calculated_at IS 'When this summary was calculated';
COMMENT ON COLUMN property_financial_summary.data_complete IS 'Whether all required data was available';

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Verify table creation
DO $$
BEGIN
  IF EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name = 'property_financial_summary'
  ) THEN
    RAISE NOTICE 'property_financial_summary table created successfully';
  ELSE
    RAISE EXCEPTION 'property_financial_summary table creation failed';
  END IF;
END $$;

-- ============================================================================
-- USAGE EXAMPLES (for developers)
-- ============================================================================

-- Example 1: Insert financial summary for a property
-- INSERT INTO property_financial_summary (
--   property_id, summary_date,
--   gross_revenue, total_expenses, noi, noi_margin,
--   annual_debt_service, dscr, ltv,
--   total_units, occupied_units, occupancy_rate, vacant_units,
--   tenant_count, average_lease_term_months, expiring_leases_12mo,
--   cap_rate, roi_pct,
--   expense_per_sqft, revenue_per_sqft, rent_per_occupied_sqft,
--   avg_rent_per_unit, rent_growth_pct_yoy, expense_ratio,
--   below_market_rent, above_average_expense, lease_expiration_risk
-- ) VALUES (
--   '123e4567-e89b-12d3-a456-426614174000', CURRENT_DATE,
--   1200000.00, 350000.00, 850000.00, 0.708,
--   600000.00, 1.42, 0.65,
--   50, 46, 0.92, 4,
--   46, 24.5, 12,
--   0.057, 12.50,
--   7.00, 24.00, 26.09,
--   2500.00, 3.50, 0.292,
--   false, false, true
-- );

-- Example 2: Query most recent summary for a property
-- SELECT 
--   summary_date, summary_month,
--   noi, noi_margin, dscr,
--   occupancy_rate, tenant_count,
--   cap_rate, roi_pct,
--   below_market_rent, above_average_expense, lease_expiration_risk
-- FROM property_financial_summary
-- WHERE property_id = '123e4567-e89b-12d3-a456-426614174000'
-- ORDER BY summary_date DESC
-- LIMIT 1;

-- Example 3: Dashboard KPI query (no joins needed!)
-- SELECT 
--   p.name as property_name,
--   pfs.noi,
--   pfs.occupancy_rate,
--   pfs.dscr,
--   pfs.cap_rate,
--   pfs.expiring_leases_12mo,
--   pfs.below_market_rent,
--   pfs.above_average_expense
-- FROM property_financial_summary pfs
-- JOIN properties p ON p.id = pfs.property_id
-- WHERE pfs.summary_month = TO_CHAR(CURRENT_DATE, 'YYYY-MM')
-- ORDER BY pfs.noi DESC;

-- Example 4: Properties with risk flags
-- SELECT 
--   p.name as property_name,
--   pfs.summary_date,
--   pfs.noi,
--   pfs.occupancy_rate,
--   CASE 
--     WHEN pfs.below_market_rent THEN 'Below Market Rent'
--     WHEN pfs.above_average_expense THEN 'High Expenses'
--     WHEN pfs.lease_expiration_risk THEN 'Lease Expiration Risk'
--   END as risk_type
-- FROM property_financial_summary pfs
-- JOIN properties p ON p.id = pfs.property_id
-- WHERE (pfs.below_market_rent = true 
--     OR pfs.above_average_expense = true 
--     OR pfs.lease_expiration_risk = true)
--   AND pfs.summary_month = TO_CHAR(CURRENT_DATE, 'YYYY-MM')
-- ORDER BY pfs.noi DESC;

-- Example 5: Portfolio performance summary
-- SELECT 
--   COUNT(*) as property_count,
--   SUM(noi) as total_noi,
--   AVG(occupancy_rate) as avg_occupancy,
--   AVG(dscr) as avg_dscr,
--   AVG(cap_rate) as avg_cap_rate,
--   SUM(CASE WHEN below_market_rent THEN 1 ELSE 0 END) as below_market_count,
--   SUM(CASE WHEN above_average_expense THEN 1 ELSE 0 END) as high_expense_count,
--   SUM(CASE WHEN lease_expiration_risk THEN 1 ELSE 0 END) as lease_risk_count
-- FROM property_financial_summary
-- WHERE summary_month = TO_CHAR(CURRENT_DATE, 'YYYY-MM')
--   AND data_complete = true;

-- Example 6: Historical trend for a property
-- SELECT 
--   summary_month,
--   noi,
--   occupancy_rate,
--   dscr,
--   tenant_count,
--   expiring_leases_12mo
-- FROM property_financial_summary
-- WHERE property_id = '123e4567-e89b-12d3-a456-426614174000'
-- ORDER BY summary_date DESC
-- LIMIT 12; -- Last 12 months

-- Example 7: Top performing properties
-- SELECT 
--   p.name as property_name,
--   pfs.noi,
--   pfs.roi_pct,
--   pfs.cap_rate,
--   pfs.occupancy_rate,
--   pfs.rent_growth_pct_yoy
-- FROM property_financial_summary pfs
-- JOIN properties p ON p.id = pfs.property_id
-- WHERE pfs.summary_month = TO_CHAR(CURRENT_DATE, 'YYYY-MM')
--   AND pfs.data_complete = true
-- ORDER BY pfs.roi_pct DESC
-- LIMIT 10;

-- Example 8: Upsert (update or insert) for batch processing
-- INSERT INTO property_financial_summary (
--   property_id, summary_date, noi, occupancy_rate, dscr
-- ) VALUES (
--   '123e4567-e89b-12d3-a456-426614174000', CURRENT_DATE, 850000.00, 0.92, 1.42
-- )
-- ON CONFLICT (property_id, summary_month)
-- DO UPDATE SET
--   noi = EXCLUDED.noi,
--   occupancy_rate = EXCLUDED.occupancy_rate,
--   dscr = EXCLUDED.dscr,
--   calculated_at = CURRENT_TIMESTAMP;

-- Example 9: Month-over-month comparison
-- WITH current_month AS (
--   SELECT * FROM property_financial_summary 
--   WHERE property_id = '123e4567-e89b-12d3-a456-426614174000'
--     AND summary_month = TO_CHAR(CURRENT_DATE, 'YYYY-MM')
-- ),
-- previous_month AS (
--   SELECT * FROM property_financial_summary 
--   WHERE property_id = '123e4567-e89b-12d3-a456-426614174000'
--     AND summary_month = TO_CHAR(CURRENT_DATE - INTERVAL '1 month', 'YYYY-MM')
-- )
-- SELECT 
--   c.summary_month as current_month,
--   c.noi as current_noi,
--   p.noi as previous_noi,
--   ((c.noi - p.noi) / p.noi * 100) as noi_change_pct,
--   c.occupancy_rate as current_occupancy,
--   p.occupancy_rate as previous_occupancy,
--   (c.occupancy_rate - p.occupancy_rate) as occupancy_change
-- FROM current_month c
-- CROSS JOIN previous_month p;


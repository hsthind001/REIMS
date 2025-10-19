-- Migration 009: Create Exit Strategy Analysis Table
-- Purpose: Store exit strategy analysis for hold, refinance, and sale scenarios
-- Required by: BR-004 (exit strategy intelligence)
-- Date: 2025-10-12

-- ============================================================================
-- EXIT_STRATEGY_ANALYSIS TABLE: Strategic analysis for property disposition
-- ============================================================================

CREATE TABLE IF NOT EXISTS exit_strategy_analysis (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
  
  -- Analysis Date
  analysis_date DATE NOT NULL,
  analysis_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  
  -- Market Data Used in Analysis
  market_cap_rate DECIMAL(5, 3), -- e.g., 0.065 (6.5%)
  market_mortgage_rate DECIMAL(5, 3), -- e.g., 0.055 (5.5%)
  property_condition_adjustment DECIMAL(3, 2), -- 0.90 to 1.10 (90% to 110%)
  location_premium DECIMAL(3, 2), -- e.g., 1.05 (5% premium)
  
  -- HOLD Scenario Analysis
  hold_projected_noi_5yr DECIMAL(15, 2)[], -- Array of 5 years NOI projections
  hold_irr DECIMAL(5, 3), -- Internal Rate of Return
  hold_total_return DECIMAL(15, 2), -- Total return over hold period
  hold_terminal_value DECIMAL(15, 2), -- Property value at end of hold period
  hold_pros TEXT[], -- Array of advantages
  hold_cons TEXT[], -- Array of disadvantages
  
  -- REFINANCE Scenario Analysis
  refinance_new_loan_amount DECIMAL(15, 2),
  refinance_new_rate DECIMAL(5, 3), -- New interest rate
  refinance_cash_out DECIMAL(15, 2), -- Cash out amount
  refinance_monthly_savings DECIMAL(10, 2), -- Monthly payment savings
  refinance_new_dscr DECIMAL(4, 2), -- New Debt Service Coverage Ratio
  refinance_feasible BOOLEAN, -- Can refinance at >= 1.25 DSCR
  refinance_pros TEXT[], -- Array of advantages
  refinance_cons TEXT[], -- Array of disadvantages
  
  -- SALE Scenario Analysis
  sale_estimated_price DECIMAL(15, 2),
  sale_transaction_costs DECIMAL(15, 2), -- Broker fees, closing costs
  sale_loan_payoff DECIMAL(15, 2), -- Remaining loan balance
  sale_net_proceeds DECIMAL(15, 2), -- After costs and payoff
  sale_total_return_pct DECIMAL(5, 2), -- Total return as percentage
  sale_annualized_return DECIMAL(5, 3), -- Annualized return (IRR)
  sale_pros TEXT[], -- Array of advantages
  sale_cons TEXT[], -- Array of disadvantages
  
  -- Recommendation
  recommended_strategy VARCHAR(50), -- 'hold', 'refinance', 'sale'
  recommendation_confidence DECIMAL(3, 2), -- 0.00 to 1.00
  recommendation_rationale TEXT,
  
  -- Analysis Metadata
  analyst_id UUID, -- User who requested analysis
  analysis_complete BOOLEAN DEFAULT true,
  
  -- Audit
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEXES: Optimized for property lookups and reporting
-- ============================================================================

-- Property-specific analysis history
CREATE INDEX idx_exit_property_id ON exit_strategy_analysis(property_id);

-- Temporal queries (most recent first)
CREATE INDEX idx_exit_analysis_date ON exit_strategy_analysis(analysis_date DESC);

-- Filter by recommendation
CREATE INDEX idx_exit_recommendation ON exit_strategy_analysis(recommended_strategy);

-- Combined property + date (common query pattern)
CREATE INDEX idx_exit_property_date ON exit_strategy_analysis(property_id, analysis_date DESC);

-- High-confidence recommendations
CREATE INDEX idx_exit_confidence ON exit_strategy_analysis(recommendation_confidence) 
  WHERE recommendation_confidence >= 0.70;

-- ============================================================================
-- CONSTRAINTS: Data validation and business rules
-- ============================================================================

-- Market cap rate must be positive
ALTER TABLE exit_strategy_analysis
  ADD CONSTRAINT chk_market_cap_rate 
  CHECK (market_cap_rate IS NULL OR market_cap_rate > 0);

-- Market mortgage rate must be positive
ALTER TABLE exit_strategy_analysis
  ADD CONSTRAINT chk_market_mortgage_rate 
  CHECK (market_mortgage_rate IS NULL OR market_mortgage_rate > 0);

-- Property condition adjustment between 0.90 and 1.10 (90% to 110%)
ALTER TABLE exit_strategy_analysis
  ADD CONSTRAINT chk_property_condition 
  CHECK (property_condition_adjustment IS NULL OR 
         (property_condition_adjustment >= 0.90 AND property_condition_adjustment <= 1.10));

-- Location premium must be positive
ALTER TABLE exit_strategy_analysis
  ADD CONSTRAINT chk_location_premium 
  CHECK (location_premium IS NULL OR location_premium > 0);

-- Hold IRR must be reasonable (-1.00 to 1.00, or -100% to 100%)
ALTER TABLE exit_strategy_analysis
  ADD CONSTRAINT chk_hold_irr 
  CHECK (hold_irr IS NULL OR (hold_irr >= -1.00 AND hold_irr <= 1.00));

-- Refinance new rate must be positive
ALTER TABLE exit_strategy_analysis
  ADD CONSTRAINT chk_refinance_rate 
  CHECK (refinance_new_rate IS NULL OR refinance_new_rate > 0);

-- Refinance DSCR must be positive (typically >= 1.25 for feasibility)
ALTER TABLE exit_strategy_analysis
  ADD CONSTRAINT chk_refinance_dscr 
  CHECK (refinance_new_dscr IS NULL OR refinance_new_dscr > 0);

-- Sale total return percentage must be reasonable
ALTER TABLE exit_strategy_analysis
  ADD CONSTRAINT chk_sale_return_pct 
  CHECK (sale_total_return_pct IS NULL OR 
         (sale_total_return_pct >= -100.00 AND sale_total_return_pct <= 1000.00));

-- Sale annualized return must be reasonable
ALTER TABLE exit_strategy_analysis
  ADD CONSTRAINT chk_sale_annualized_return 
  CHECK (sale_annualized_return IS NULL OR 
         (sale_annualized_return >= -1.00 AND sale_annualized_return <= 1.00));

-- Recommendation confidence between 0 and 1
ALTER TABLE exit_strategy_analysis
  ADD CONSTRAINT chk_recommendation_confidence 
  CHECK (recommendation_confidence IS NULL OR 
         (recommendation_confidence >= 0.00 AND recommendation_confidence <= 1.00));

-- Valid recommendation strategy
ALTER TABLE exit_strategy_analysis
  ADD CONSTRAINT chk_recommended_strategy 
  CHECK (recommended_strategy IS NULL OR 
         recommended_strategy IN ('hold', 'refinance', 'sale', 'insufficient_data'));

-- Analysis date should not be in the future
ALTER TABLE exit_strategy_analysis
  ADD CONSTRAINT chk_analysis_date 
  CHECK (analysis_date <= CURRENT_DATE);

-- ============================================================================
-- TRIGGERS: Auto-update timestamp
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_exit_strategy_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update timestamp on row modification
CREATE TRIGGER trigger_update_exit_strategy_timestamp
  BEFORE UPDATE ON exit_strategy_analysis
  FOR EACH ROW
  EXECUTE FUNCTION update_exit_strategy_timestamp();

-- ============================================================================
-- TABLE COMMENTS: Documentation for database administrators
-- ============================================================================

COMMENT ON TABLE exit_strategy_analysis IS 'Exit strategy analysis for properties. Stores hold, refinance, and sale scenarios. Required for BR-004 exit strategy intelligence. Created on-demand when user requests analysis.';

COMMENT ON COLUMN exit_strategy_analysis.property_id IS 'Property being analyzed';
COMMENT ON COLUMN exit_strategy_analysis.analysis_date IS 'Date the analysis was performed';
COMMENT ON COLUMN exit_strategy_analysis.analysis_timestamp IS 'Timestamp of analysis completion';

COMMENT ON COLUMN exit_strategy_analysis.market_cap_rate IS 'Market capitalization rate used in analysis (e.g., 0.065 for 6.5%)';
COMMENT ON COLUMN exit_strategy_analysis.market_mortgage_rate IS 'Current market mortgage rate (e.g., 0.055 for 5.5%)';
COMMENT ON COLUMN exit_strategy_analysis.property_condition_adjustment IS 'Adjustment factor for property condition (0.90 to 1.10)';
COMMENT ON COLUMN exit_strategy_analysis.location_premium IS 'Location premium multiplier (e.g., 1.05 for 5% premium)';

COMMENT ON COLUMN exit_strategy_analysis.hold_projected_noi_5yr IS 'Array of 5 years projected NOI values';
COMMENT ON COLUMN exit_strategy_analysis.hold_irr IS 'Internal Rate of Return for hold scenario';
COMMENT ON COLUMN exit_strategy_analysis.hold_total_return IS 'Total dollar return over hold period';
COMMENT ON COLUMN exit_strategy_analysis.hold_terminal_value IS 'Estimated property value at end of hold period';
COMMENT ON COLUMN exit_strategy_analysis.hold_pros IS 'Array of advantages for holding the property';
COMMENT ON COLUMN exit_strategy_analysis.hold_cons IS 'Array of disadvantages for holding the property';

COMMENT ON COLUMN exit_strategy_analysis.refinance_new_loan_amount IS 'New loan amount if refinanced';
COMMENT ON COLUMN exit_strategy_analysis.refinance_new_rate IS 'New interest rate if refinanced';
COMMENT ON COLUMN exit_strategy_analysis.refinance_cash_out IS 'Cash-out amount from refinancing';
COMMENT ON COLUMN exit_strategy_analysis.refinance_monthly_savings IS 'Monthly payment savings from refinancing';
COMMENT ON COLUMN exit_strategy_analysis.refinance_new_dscr IS 'New Debt Service Coverage Ratio (must be >= 1.25 for CMBS)';
COMMENT ON COLUMN exit_strategy_analysis.refinance_feasible IS 'Whether refinancing is feasible at >= 1.25 DSCR';
COMMENT ON COLUMN exit_strategy_analysis.refinance_pros IS 'Array of advantages for refinancing';
COMMENT ON COLUMN exit_strategy_analysis.refinance_cons IS 'Array of disadvantages for refinancing';

COMMENT ON COLUMN exit_strategy_analysis.sale_estimated_price IS 'Estimated sale price';
COMMENT ON COLUMN exit_strategy_analysis.sale_transaction_costs IS 'Total transaction costs (broker fees, closing costs)';
COMMENT ON COLUMN exit_strategy_analysis.sale_loan_payoff IS 'Remaining loan balance to pay off';
COMMENT ON COLUMN exit_strategy_analysis.sale_net_proceeds IS 'Net proceeds after costs and loan payoff';
COMMENT ON COLUMN exit_strategy_analysis.sale_total_return_pct IS 'Total return as percentage';
COMMENT ON COLUMN exit_strategy_analysis.sale_annualized_return IS 'Annualized return (IRR)';
COMMENT ON COLUMN exit_strategy_analysis.sale_pros IS 'Array of advantages for selling';
COMMENT ON COLUMN exit_strategy_analysis.sale_cons IS 'Array of disadvantages for selling';

COMMENT ON COLUMN exit_strategy_analysis.recommended_strategy IS 'Recommended strategy: hold, refinance, sale, or insufficient_data';
COMMENT ON COLUMN exit_strategy_analysis.recommendation_confidence IS 'Confidence in recommendation (0.00 to 1.00, >= 0.70 preferred)';
COMMENT ON COLUMN exit_strategy_analysis.recommendation_rationale IS 'Explanation of why this strategy is recommended';

COMMENT ON COLUMN exit_strategy_analysis.analyst_id IS 'User who requested the analysis';
COMMENT ON COLUMN exit_strategy_analysis.analysis_complete IS 'Whether analysis completed successfully';
COMMENT ON COLUMN exit_strategy_analysis.updated_at IS 'Last update timestamp';

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Verify table creation
DO $$
BEGIN
  IF EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name = 'exit_strategy_analysis'
  ) THEN
    RAISE NOTICE 'exit_strategy_analysis table created successfully';
  ELSE
    RAISE EXCEPTION 'exit_strategy_analysis table creation failed';
  END IF;
END $$;

-- ============================================================================
-- USAGE EXAMPLES (for developers)
-- ============================================================================

-- Example 1: Insert complete exit strategy analysis
-- INSERT INTO exit_strategy_analysis (
--   property_id, analysis_date,
--   market_cap_rate, market_mortgage_rate, property_condition_adjustment, location_premium,
--   hold_projected_noi_5yr, hold_irr, hold_total_return, hold_terminal_value,
--   hold_pros, hold_cons,
--   refinance_new_loan_amount, refinance_new_rate, refinance_cash_out,
--   refinance_monthly_savings, refinance_new_dscr, refinance_feasible,
--   refinance_pros, refinance_cons,
--   sale_estimated_price, sale_transaction_costs, sale_loan_payoff,
--   sale_net_proceeds, sale_total_return_pct, sale_annualized_return,
--   sale_pros, sale_cons,
--   recommended_strategy, recommendation_confidence, recommendation_rationale,
--   analyst_id
-- ) VALUES (
--   '123e4567-e89b-12d3-a456-426614174000', CURRENT_DATE,
--   0.065, 0.055, 0.95, 1.05,
--   ARRAY[850000, 875000, 900000, 925000, 950000], 0.082, 2500000, 15000000,
--   ARRAY['Strong market fundamentals', 'Consistent cash flow', 'Long-term appreciation'],
--   ARRAY['Capital tied up', 'Property management burden'],
--   10000000, 0.050, 1500000,
--   5000, 1.45, true,
--   ARRAY['Unlock equity', 'Lower monthly payments', 'Improve cash flow'],
--   ARRAY['Closing costs', 'Extended loan term'],
--   14500000, 725000, 9000000,
--   4775000, 38.20, 0.078,
--   ARRAY['Immediate liquidity', 'Strong market conditions', 'High returns'],
--   ARRAY['Capital gains tax', 'Loss of future appreciation'],
--   'hold', 0.85, 'Property shows strong fundamentals with consistent NOI growth. Hold scenario provides best long-term returns.',
--   'analyst-uuid-here'
-- );

-- Example 2: Query most recent analysis for a property
-- SELECT 
--   analysis_date,
--   recommended_strategy,
--   recommendation_confidence,
--   hold_irr,
--   sale_annualized_return,
--   refinance_feasible
-- FROM exit_strategy_analysis
-- WHERE property_id = '123e4567-e89b-12d3-a456-426614174000'
-- ORDER BY analysis_date DESC
-- LIMIT 1;

-- Example 3: Compare scenarios for a property
-- SELECT 
--   analysis_date,
--   'Hold' as scenario,
--   hold_irr as irr,
--   hold_total_return as total_return,
--   UNNEST(hold_pros) as pros
-- FROM exit_strategy_analysis
-- WHERE property_id = '123e4567-e89b-12d3-a456-426614174000'
-- UNION ALL
-- SELECT 
--   analysis_date,
--   'Sale' as scenario,
--   sale_annualized_return as irr,
--   sale_net_proceeds as total_return,
--   UNNEST(sale_pros) as pros
-- FROM exit_strategy_analysis
-- WHERE property_id = '123e4567-e89b-12d3-a456-426614174000'
-- ORDER BY analysis_date DESC, scenario;

-- Example 4: Properties recommended for sale
-- SELECT 
--   p.name as property_name,
--   esa.sale_estimated_price,
--   esa.sale_net_proceeds,
--   esa.sale_annualized_return,
--   esa.recommendation_confidence,
--   esa.analysis_date
-- FROM exit_strategy_analysis esa
-- JOIN properties p ON p.id = esa.property_id
-- WHERE esa.recommended_strategy = 'sale'
--   AND esa.recommendation_confidence >= 0.70
--   AND esa.analysis_date >= CURRENT_DATE - INTERVAL '90 days'
-- ORDER BY esa.sale_annualized_return DESC;

-- Example 5: Refinancing opportunities
-- SELECT 
--   p.name as property_name,
--   esa.refinance_new_loan_amount,
--   esa.refinance_cash_out,
--   esa.refinance_monthly_savings,
--   esa.refinance_new_dscr,
--   esa.analysis_date
-- FROM exit_strategy_analysis esa
-- JOIN properties p ON p.id = esa.property_id
-- WHERE esa.recommended_strategy = 'refinance'
--   AND esa.refinance_feasible = true
--   AND esa.refinance_new_dscr >= 1.25
--   AND esa.recommendation_confidence >= 0.70
-- ORDER BY esa.refinance_cash_out DESC;

-- Example 6: Historical analysis tracking
-- SELECT 
--   analysis_date,
--   recommended_strategy,
--   recommendation_confidence,
--   hold_irr,
--   sale_annualized_return
-- FROM exit_strategy_analysis
-- WHERE property_id = '123e4567-e89b-12d3-a456-426614174000'
-- ORDER BY analysis_date DESC;

-- Example 7: Working with NOI projections array
-- SELECT 
--   property_id,
--   analysis_date,
--   UNNEST(hold_projected_noi_5yr) as projected_noi,
--   generate_series(1, ARRAY_LENGTH(hold_projected_noi_5yr, 1)) as year
-- FROM exit_strategy_analysis
-- WHERE property_id = '123e4567-e89b-12d3-a456-426614174000'
--   AND analysis_date = (
--     SELECT MAX(analysis_date) 
--     FROM exit_strategy_analysis 
--     WHERE property_id = '123e4567-e89b-12d3-a456-426614174000'
--   );


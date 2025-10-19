-- Migration 008: Create Anomaly Detection Results Table
-- Purpose: Store historical anomaly detection analysis results
-- Required by: BR-008 (anomaly detection engine)
-- Date: 2025-10-12

-- ============================================================================
-- ANOMALY_DETECTION_RESULTS TABLE: Statistical anomaly detection results
-- ============================================================================

CREATE TABLE IF NOT EXISTS anomaly_detection_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
  
  -- Metric Being Analyzed
  metric_name VARCHAR(100) NOT NULL, -- 'noi', 'occupancy', 'revenue', 'expenses'
  metric_history_start_date DATE,
  metric_history_end_date DATE,
  data_points_analyzed INTEGER, -- How many historical values were analyzed
  
  -- Z-Score Analysis (Statistical Outlier Detection)
  zscore_detected BOOLEAN DEFAULT false,
  zscore_threshold DECIMAL(5, 2), -- Typically 2.0 or 3.0 (standard deviations)
  zscore_values DECIMAL(5, 2)[], -- Array of z-scores for each data point
  zscore_anomalies INTEGER, -- Count of anomalies found by z-score
  
  -- CUSUM Analysis (Trend Shift Detection)
  cusum_detected BOOLEAN DEFAULT false,
  cusum_threshold DECIMAL(10, 2), -- Typically 5.0
  cusum_direction VARCHAR(20), -- 'upward', 'downward', 'both'
  cusum_anomalies INTEGER, -- Count of anomalies found by CUSUM
  
  -- Results Summary
  anomalies_found BOOLEAN DEFAULT false,
  anomaly_confidence DECIMAL(3, 2), -- Overall confidence (0.00 to 1.00)
  anomaly_type VARCHAR(50), -- 'outlier', 'trend_shift', 'level_change', 'seasonal'
  
  -- Detected Anomaly Details (Arrays for multiple anomalies)
  anomaly_values DECIMAL(18, 2)[], -- The actual anomalous values
  anomaly_dates DATE[], -- When they occurred
  anomaly_descriptions TEXT[], -- Human-readable descriptions
  
  -- Business Impact
  requires_review BOOLEAN DEFAULT false,
  requires_alert BOOLEAN DEFAULT false,
  
  -- Analysis Parameters
  lookback_months INTEGER DEFAULT 12,
  analysis_method VARCHAR(50), -- 'z_score', 'cusum', 'combination', 'ml_model'
  
  -- Timing
  analysis_date DATE NOT NULL,
  analysis_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  analysis_duration_seconds DECIMAL(10, 2)
);

-- ============================================================================
-- INDEXES: Optimized for anomaly queries and reports
-- ============================================================================

-- Property-specific queries
CREATE INDEX idx_anomaly_property_id ON anomaly_detection_results(property_id);

-- Metric-specific analysis
CREATE INDEX idx_anomaly_metric_name ON anomaly_detection_results(metric_name);

-- Filter by detection status
CREATE INDEX idx_anomaly_detected ON anomaly_detection_results(anomalies_found);

-- Temporal queries (most recent analyses)
CREATE INDEX idx_anomaly_analysis_date ON anomaly_detection_results(analysis_date DESC);

-- Combined property + metric lookups (most common query pattern)
CREATE INDEX idx_anomaly_property_metric ON anomaly_detection_results(property_id, metric_name);

-- Review queue queries
CREATE INDEX idx_anomaly_requires_review ON anomaly_detection_results(requires_review) WHERE requires_review = true;

-- Alert generation queries
CREATE INDEX idx_anomaly_requires_alert ON anomaly_detection_results(requires_alert) WHERE requires_alert = true;

-- ============================================================================
-- CONSTRAINTS: Data validation
-- ============================================================================

-- Confidence must be between 0 and 1
ALTER TABLE anomaly_detection_results
  ADD CONSTRAINT chk_anomaly_confidence 
  CHECK (anomaly_confidence >= 0.00 AND anomaly_confidence <= 1.00);

-- Z-score threshold must be positive
ALTER TABLE anomaly_detection_results
  ADD CONSTRAINT chk_zscore_threshold 
  CHECK (zscore_threshold IS NULL OR zscore_threshold > 0);

-- CUSUM threshold must be positive
ALTER TABLE anomaly_detection_results
  ADD CONSTRAINT chk_cusum_threshold 
  CHECK (cusum_threshold IS NULL OR cusum_threshold > 0);

-- Data points analyzed must be positive
ALTER TABLE anomaly_detection_results
  ADD CONSTRAINT chk_data_points 
  CHECK (data_points_analyzed IS NULL OR data_points_analyzed > 0);

-- Lookback months must be positive
ALTER TABLE anomaly_detection_results
  ADD CONSTRAINT chk_lookback_months 
  CHECK (lookback_months > 0);

-- Analysis duration must be non-negative
ALTER TABLE anomaly_detection_results
  ADD CONSTRAINT chk_analysis_duration 
  CHECK (analysis_duration_seconds IS NULL OR analysis_duration_seconds >= 0);

-- Valid CUSUM direction
ALTER TABLE anomaly_detection_results
  ADD CONSTRAINT chk_cusum_direction 
  CHECK (cusum_direction IS NULL OR cusum_direction IN ('upward', 'downward', 'both'));

-- Valid anomaly type
ALTER TABLE anomaly_detection_results
  ADD CONSTRAINT chk_anomaly_type 
  CHECK (anomaly_type IS NULL OR anomaly_type IN ('outlier', 'trend_shift', 'level_change', 'seasonal', 'multiple'));

-- Valid analysis method
ALTER TABLE anomaly_detection_results
  ADD CONSTRAINT chk_analysis_method 
  CHECK (analysis_method IN ('z_score', 'cusum', 'combination', 'ml_model', 'ensemble'));

-- Analysis date should not be in the future
ALTER TABLE anomaly_detection_results
  ADD CONSTRAINT chk_analysis_date 
  CHECK (analysis_date <= CURRENT_DATE);

-- ============================================================================
-- TABLE COMMENTS: Documentation for database administrators
-- ============================================================================

COMMENT ON TABLE anomaly_detection_results IS 'Historical anomaly detection analysis results. Populated by nightly job at 2 AM. Required for BR-008 anomaly detection engine.';

COMMENT ON COLUMN anomaly_detection_results.property_id IS 'Property being analyzed';
COMMENT ON COLUMN anomaly_detection_results.metric_name IS 'Financial metric analyzed (noi, occupancy, revenue, expenses)';
COMMENT ON COLUMN anomaly_detection_results.metric_history_start_date IS 'Start date of historical data window';
COMMENT ON COLUMN anomaly_detection_results.metric_history_end_date IS 'End date of historical data window';
COMMENT ON COLUMN anomaly_detection_results.data_points_analyzed IS 'Number of historical data points in analysis window';

COMMENT ON COLUMN anomaly_detection_results.zscore_detected IS 'True if Z-score method detected anomalies';
COMMENT ON COLUMN anomaly_detection_results.zscore_threshold IS 'Standard deviation threshold (typically 2.0 or 3.0)';
COMMENT ON COLUMN anomaly_detection_results.zscore_values IS 'Array of z-scores for each data point';
COMMENT ON COLUMN anomaly_detection_results.zscore_anomalies IS 'Count of anomalies found by z-score method';

COMMENT ON COLUMN anomaly_detection_results.cusum_detected IS 'True if CUSUM method detected trend shifts';
COMMENT ON COLUMN anomaly_detection_results.cusum_threshold IS 'CUSUM threshold for trend detection (typically 5.0)';
COMMENT ON COLUMN anomaly_detection_results.cusum_direction IS 'Direction of trend shift: upward, downward, both';
COMMENT ON COLUMN anomaly_detection_results.cusum_anomalies IS 'Count of anomalies found by CUSUM method';

COMMENT ON COLUMN anomaly_detection_results.anomalies_found IS 'True if any anomalies detected by any method';
COMMENT ON COLUMN anomaly_detection_results.anomaly_confidence IS 'Overall confidence score (0.00 to 1.00)';
COMMENT ON COLUMN anomaly_detection_results.anomaly_type IS 'Type of anomaly: outlier, trend_shift, level_change, seasonal';

COMMENT ON COLUMN anomaly_detection_results.anomaly_values IS 'Array of anomalous metric values detected';
COMMENT ON COLUMN anomaly_detection_results.anomaly_dates IS 'Array of dates when anomalies occurred';
COMMENT ON COLUMN anomaly_detection_results.anomaly_descriptions IS 'Array of human-readable descriptions for each anomaly';

COMMENT ON COLUMN anomaly_detection_results.requires_review IS 'True if anomaly requires human review';
COMMENT ON COLUMN anomaly_detection_results.requires_alert IS 'True if committee alert should be generated';

COMMENT ON COLUMN anomaly_detection_results.lookback_months IS 'Number of months of historical data analyzed';
COMMENT ON COLUMN anomaly_detection_results.analysis_method IS 'Method used: z_score, cusum, combination, ml_model';

COMMENT ON COLUMN anomaly_detection_results.analysis_date IS 'Date the analysis was performed';
COMMENT ON COLUMN anomaly_detection_results.analysis_timestamp IS 'Timestamp of analysis completion';
COMMENT ON COLUMN anomaly_detection_results.analysis_duration_seconds IS 'Time taken to complete analysis';

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Verify table creation
DO $$
BEGIN
  IF EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name = 'anomaly_detection_results'
  ) THEN
    RAISE NOTICE 'anomaly_detection_results table created successfully';
  ELSE
    RAISE EXCEPTION 'anomaly_detection_results table creation failed';
  END IF;
END $$;

-- ============================================================================
-- USAGE EXAMPLES (for developers)
-- ============================================================================

-- Example 1: Insert NOI anomaly detection result
-- INSERT INTO anomaly_detection_results (
--   property_id, metric_name,
--   metric_history_start_date, metric_history_end_date,
--   data_points_analyzed,
--   zscore_detected, zscore_threshold, zscore_values, zscore_anomalies,
--   anomalies_found, anomaly_confidence, anomaly_type,
--   anomaly_values, anomaly_dates, anomaly_descriptions,
--   requires_review, requires_alert,
--   lookback_months, analysis_method, analysis_date, analysis_duration_seconds
-- ) VALUES (
--   '123e4567-e89b-12d3-a456-426614174000', 'noi',
--   '2024-01-01', '2024-12-31', 12,
--   true, 2.5, ARRAY[0.5, 1.2, 3.8, 1.1, 0.9, 1.4, 0.7, 1.0, 2.1, 0.8, 1.3, 1.5], 1,
--   true, 0.85, 'outlier',
--   ARRAY[85000.00], ARRAY['2024-03-15'::DATE], ARRAY['NOI dropped 35% below expected value'],
--   true, true,
--   12, 'z_score', CURRENT_DATE, 2.34
-- );

-- Example 2: Insert CUSUM trend shift detection
-- INSERT INTO anomaly_detection_results (
--   property_id, metric_name,
--   cusum_detected, cusum_threshold, cusum_direction, cusum_anomalies,
--   anomalies_found, anomaly_confidence, anomaly_type,
--   anomaly_descriptions, requires_review,
--   analysis_method, analysis_date
-- ) VALUES (
--   '123e4567-e89b-12d3-a456-426614174000', 'occupancy',
--   true, 5.0, 'downward', 1,
--   true, 0.92, 'trend_shift',
--   ARRAY['Sustained downward trend in occupancy detected starting Q2'],
--   true,
--   'cusum', CURRENT_DATE
-- );

-- Example 3: Query recent anomalies for a property
-- SELECT 
--   analysis_date,
--   metric_name,
--   anomaly_type,
--   anomaly_confidence,
--   UNNEST(anomaly_descriptions) as description,
--   requires_alert
-- FROM anomaly_detection_results
-- WHERE property_id = '123e4567-e89b-12d3-a456-426614174000'
--   AND anomalies_found = true
--   AND analysis_date >= CURRENT_DATE - INTERVAL '90 days'
-- ORDER BY analysis_date DESC;

-- Example 4: Get all properties requiring review
-- SELECT 
--   p.name as property_name,
--   adr.metric_name,
--   adr.anomaly_type,
--   adr.anomaly_confidence,
--   adr.analysis_date
-- FROM anomaly_detection_results adr
-- JOIN properties p ON p.id = adr.property_id
-- WHERE adr.requires_review = true
--   AND adr.analysis_date >= CURRENT_DATE - INTERVAL '7 days'
-- ORDER BY adr.anomaly_confidence DESC, adr.analysis_date DESC;

-- Example 5: Anomaly detection summary by metric
-- SELECT 
--   metric_name,
--   COUNT(*) as total_analyses,
--   SUM(CASE WHEN anomalies_found THEN 1 ELSE 0 END) as anomalies_detected,
--   AVG(CASE WHEN anomalies_found THEN anomaly_confidence END) as avg_confidence,
--   AVG(analysis_duration_seconds) as avg_duration_seconds
-- FROM anomaly_detection_results
-- WHERE analysis_date >= CURRENT_DATE - INTERVAL '30 days'
-- GROUP BY metric_name
-- ORDER BY anomalies_detected DESC;

-- Example 6: Working with array data
-- SELECT 
--   property_id,
--   metric_name,
--   UNNEST(anomaly_dates) as anomaly_date,
--   UNNEST(anomaly_values) as anomaly_value,
--   UNNEST(anomaly_descriptions) as description
-- FROM anomaly_detection_results
-- WHERE anomalies_found = true
--   AND metric_name = 'noi'
--   AND analysis_date >= CURRENT_DATE - INTERVAL '30 days'
-- ORDER BY anomaly_date DESC;

-- Example 7: Z-score analysis details
-- SELECT 
--   property_id,
--   metric_name,
--   zscore_threshold,
--   zscore_anomalies,
--   ARRAY_LENGTH(zscore_values, 1) as total_points,
--   (zscore_anomalies::FLOAT / ARRAY_LENGTH(zscore_values, 1)) * 100 as anomaly_percentage
-- FROM anomaly_detection_results
-- WHERE zscore_detected = true
--   AND analysis_date >= CURRENT_DATE - INTERVAL '7 days'
-- ORDER BY anomaly_percentage DESC;


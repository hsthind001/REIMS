-- ============================================================================
-- REIMS Extracted Metrics Table Migration
-- Version: 004
-- Description: Create extracted_metrics table for storing financial metrics from documents
-- Author: REIMS Development Team
-- Date: October 12, 2025
-- ============================================================================

-- Drop table if exists (for development/testing)
-- Uncomment next line if you want to recreate the table
-- DROP TABLE IF EXISTS extracted_metrics CASCADE;

-- ============================================================================
-- Main Extracted Metrics Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS extracted_metrics (
  -- Primary Key
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Foreign Keys
  document_id UUID NOT NULL REFERENCES financial_documents(id) ON DELETE CASCADE,
  property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
  
  -- ========================================================================
  -- Metric Identification
  -- ========================================================================
  metric_name VARCHAR(100) NOT NULL, -- 'gross_revenue', 'noi', 'dscr', 'occupancy', etc.
  metric_category VARCHAR(50), -- 'financial', 'occupancy', 'operational', 'expense'
  
  -- ========================================================================
  -- Extracted Value
  -- ========================================================================
  metric_value DECIMAL(18, 2),
  metric_unit VARCHAR(50), -- '$', '%', 'count', 'sqft', 'ratio'
  metric_date DATE, -- Date the metric is for (e.g., "Q3 2024")
  
  -- ========================================================================
  -- Confidence & Quality
  -- ========================================================================
  confidence_score DECIMAL(3, 2) NOT NULL, -- 0.00 to 1.00
  extraction_method VARCHAR(50) NOT NULL, -- 'table_structured', 'ocr_clear', 'pattern_match', 'ml_inference'
  
  -- ========================================================================
  -- Validation
  -- ========================================================================
  is_validated BOOLEAN DEFAULT false, -- Manual review by analyst
  validated_by UUID,
  validated_at TIMESTAMP,
  validation_notes TEXT,
  
  -- ========================================================================
  -- Anomaly Detection
  -- ========================================================================
  is_anomaly BOOLEAN DEFAULT false,
  anomaly_type VARCHAR(50), -- 'z_score', 'cusum', 'trend_shift', 'iqr_outlier'
  anomaly_score DECIMAL(5, 2), -- Z-score or similar metric
  
  -- ========================================================================
  -- Source Information
  -- ========================================================================
  source_page_number INTEGER, -- Which page in document
  source_table_number INTEGER, -- Which table on page
  source_text_snippet VARCHAR(500), -- Original text extracted
  
  -- ========================================================================
  -- Audit
  -- ========================================================================
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_by UUID
);

-- ============================================================================
-- Performance Indexes
-- ============================================================================

-- Document ID index (for fetching all metrics from a document)
CREATE INDEX IF NOT EXISTS idx_metrics_document_id 
  ON extracted_metrics(document_id);

-- Property ID index (for fetching all metrics for a property)
CREATE INDEX IF NOT EXISTS idx_metrics_property_id 
  ON extracted_metrics(property_id);

-- Metric name index (for filtering by metric type)
CREATE INDEX IF NOT EXISTS idx_metrics_metric_name 
  ON extracted_metrics(metric_name);

-- Metric date index (for time-series analysis)
CREATE INDEX IF NOT EXISTS idx_metrics_metric_date 
  ON extracted_metrics(metric_date DESC);

-- Confidence index (for filtering low-confidence metrics)
CREATE INDEX IF NOT EXISTS idx_metrics_confidence 
  ON extracted_metrics(confidence_score);

-- Anomaly index (for quick anomaly queries)
CREATE INDEX IF NOT EXISTS idx_metrics_is_anomaly 
  ON extracted_metrics(is_anomaly) 
  WHERE is_anomaly = true;

-- Composite index for property + metric queries
CREATE INDEX IF NOT EXISTS idx_metrics_property_metric 
  ON extracted_metrics(property_id, metric_name);

-- Created date index
CREATE INDEX IF NOT EXISTS idx_metrics_created_at 
  ON extracted_metrics(created_at DESC);

-- Composite index for common time-series queries
CREATE INDEX IF NOT EXISTS idx_metrics_property_date_metric 
  ON extracted_metrics(property_id, metric_date DESC, metric_name);

-- Validation status index
CREATE INDEX IF NOT EXISTS idx_metrics_validation_status 
  ON extracted_metrics(is_validated, confidence_score);

-- Category index
CREATE INDEX IF NOT EXISTS idx_metrics_category 
  ON extracted_metrics(metric_category) 
  WHERE metric_category IS NOT NULL;

-- ============================================================================
-- Constraints
-- ============================================================================

-- Confidence score must be between 0 and 1
ALTER TABLE extracted_metrics 
  DROP CONSTRAINT IF EXISTS chk_confidence;
ALTER TABLE extracted_metrics 
  ADD CONSTRAINT chk_confidence 
  CHECK (confidence_score >= 0 AND confidence_score <= 1);

-- Metric value should not be exactly zero (use NULL instead)
ALTER TABLE extracted_metrics 
  DROP CONSTRAINT IF EXISTS chk_metric_value_not_zero;
ALTER TABLE extracted_metrics 
  ADD CONSTRAINT chk_metric_value_not_zero 
  CHECK (metric_value IS NULL OR metric_value != 0);

-- Anomaly score should be reasonable
ALTER TABLE extracted_metrics 
  DROP CONSTRAINT IF EXISTS chk_anomaly_score_reasonable;
ALTER TABLE extracted_metrics 
  ADD CONSTRAINT chk_anomaly_score_reasonable 
  CHECK (anomaly_score IS NULL OR ABS(anomaly_score) <= 100);

-- Metric category must be valid
ALTER TABLE extracted_metrics 
  DROP CONSTRAINT IF EXISTS chk_valid_metric_category;
ALTER TABLE extracted_metrics 
  ADD CONSTRAINT chk_valid_metric_category 
  CHECK (metric_category IS NULL OR metric_category IN (
    'financial', 'occupancy', 'operational', 'expense', 
    'revenue', 'debt_service', 'valuation', 'ratio', 'other'
  ));

-- Extraction method must be valid
ALTER TABLE extracted_metrics 
  DROP CONSTRAINT IF EXISTS chk_valid_extraction_method;
ALTER TABLE extracted_metrics 
  ADD CONSTRAINT chk_valid_extraction_method 
  CHECK (extraction_method IN (
    'table_structured', 'ocr_clear', 'ocr_fuzzy', 'pattern_match', 
    'ml_inference', 'manual_entry', 'api_import', 'calculated'
  ));

-- Anomaly type must be valid if is_anomaly is true
ALTER TABLE extracted_metrics 
  DROP CONSTRAINT IF EXISTS chk_valid_anomaly_type;
ALTER TABLE extracted_metrics 
  ADD CONSTRAINT chk_valid_anomaly_type 
  CHECK (
    (is_anomaly = false) OR 
    (is_anomaly = true AND anomaly_type IS NOT NULL AND anomaly_type IN (
      'z_score', 'cusum', 'trend_shift', 'iqr_outlier', 'manual_flag', 'threshold_breach'
    ))
  );

-- Metric unit must be valid
ALTER TABLE extracted_metrics 
  DROP CONSTRAINT IF EXISTS chk_valid_metric_unit;
ALTER TABLE extracted_metrics 
  ADD CONSTRAINT chk_valid_metric_unit 
  CHECK (metric_unit IS NULL OR metric_unit IN (
    '$', '%', 'count', 'sqft', 'ratio', 'days', 'months', 'years', 'units'
  ));

-- Page and table numbers must be positive
ALTER TABLE extracted_metrics 
  DROP CONSTRAINT IF EXISTS chk_positive_source_numbers;
ALTER TABLE extracted_metrics 
  ADD CONSTRAINT chk_positive_source_numbers 
  CHECK (
    (source_page_number IS NULL OR source_page_number > 0) AND
    (source_table_number IS NULL OR source_table_number > 0)
  );

-- If validated, must have validator and timestamp
ALTER TABLE extracted_metrics 
  DROP CONSTRAINT IF EXISTS chk_validation_complete;
ALTER TABLE extracted_metrics 
  ADD CONSTRAINT chk_validation_complete 
  CHECK (
    (is_validated = false) OR 
    (is_validated = true AND validated_by IS NOT NULL AND validated_at IS NOT NULL)
  );

-- ============================================================================
-- Trigger for Updated Timestamp
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_extracted_metrics_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop trigger if exists
DROP TRIGGER IF EXISTS trg_extracted_metrics_updated_at ON extracted_metrics;

-- Create trigger
CREATE TRIGGER trg_extracted_metrics_updated_at
  BEFORE UPDATE ON extracted_metrics
  FOR EACH ROW
  EXECUTE FUNCTION update_extracted_metrics_updated_at();

-- ============================================================================
-- Function to Get Latest Metrics by Property
-- ============================================================================

CREATE OR REPLACE FUNCTION get_latest_metrics(p_property_id UUID)
RETURNS TABLE (
  metric_name VARCHAR(100),
  metric_value DECIMAL(18, 2),
  metric_unit VARCHAR(50),
  metric_date DATE,
  confidence_score DECIMAL(3, 2),
  is_validated BOOLEAN
) AS $$
BEGIN
  RETURN QUERY
  SELECT DISTINCT ON (em.metric_name)
    em.metric_name,
    em.metric_value,
    em.metric_unit,
    em.metric_date,
    em.confidence_score,
    em.is_validated
  FROM extracted_metrics em
  WHERE em.property_id = p_property_id
  ORDER BY em.metric_name, em.metric_date DESC NULLS LAST, em.confidence_score DESC;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Function to Detect Anomalies (Z-Score Method)
-- ============================================================================

CREATE OR REPLACE FUNCTION detect_metric_anomalies(
  p_property_id UUID,
  p_metric_name VARCHAR(100),
  p_z_threshold DECIMAL DEFAULT 3.0
)
RETURNS TABLE (
  metric_id UUID,
  metric_value DECIMAL(18, 2),
  metric_date DATE,
  z_score DECIMAL(5, 2),
  is_anomaly BOOLEAN
) AS $$
BEGIN
  RETURN QUERY
  WITH stats AS (
    SELECT 
      AVG(metric_value) as mean_value,
      STDDEV(metric_value) as stddev_value
    FROM extracted_metrics
    WHERE property_id = p_property_id
      AND metric_name = p_metric_name
      AND metric_value IS NOT NULL
  )
  SELECT 
    em.id,
    em.metric_value,
    em.metric_date,
    CASE 
      WHEN stats.stddev_value > 0 
      THEN ((em.metric_value - stats.mean_value) / stats.stddev_value)::DECIMAL(5, 2)
      ELSE 0::DECIMAL(5, 2)
    END as z_score,
    CASE 
      WHEN stats.stddev_value > 0 
      THEN ABS((em.metric_value - stats.mean_value) / stats.stddev_value) > p_z_threshold
      ELSE false
    END as is_anomaly
  FROM extracted_metrics em
  CROSS JOIN stats
  WHERE em.property_id = p_property_id
    AND em.metric_name = p_metric_name
    AND em.metric_value IS NOT NULL
  ORDER BY em.metric_date DESC;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Function to Get Metric Time Series
-- ============================================================================

CREATE OR REPLACE FUNCTION get_metric_timeseries(
  p_property_id UUID,
  p_metric_name VARCHAR(100),
  p_start_date DATE DEFAULT NULL,
  p_end_date DATE DEFAULT NULL
)
RETURNS TABLE (
  metric_date DATE,
  metric_value DECIMAL(18, 2),
  metric_unit VARCHAR(50),
  confidence_score DECIMAL(3, 2),
  document_name VARCHAR(255)
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    em.metric_date,
    em.metric_value,
    em.metric_unit,
    em.confidence_score,
    fd.file_name as document_name
  FROM extracted_metrics em
  LEFT JOIN financial_documents fd ON em.document_id = fd.id
  WHERE em.property_id = p_property_id
    AND em.metric_name = p_metric_name
    AND (p_start_date IS NULL OR em.metric_date >= p_start_date)
    AND (p_end_date IS NULL OR em.metric_date <= p_end_date)
  ORDER BY em.metric_date DESC;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Function to Calculate Alert Thresholds
-- ============================================================================

CREATE OR REPLACE FUNCTION check_metric_alerts(p_property_id UUID)
RETURNS TABLE (
  metric_name VARCHAR(100),
  metric_value DECIMAL(18, 2),
  threshold_value DECIMAL(18, 2),
  alert_type VARCHAR(50),
  severity VARCHAR(20)
) AS $$
BEGIN
  RETURN QUERY
  WITH latest_metrics AS (
    SELECT DISTINCT ON (em.metric_name)
      em.metric_name,
      em.metric_value,
      em.metric_unit
    FROM extracted_metrics em
    WHERE em.property_id = p_property_id
    ORDER BY em.metric_name, em.metric_date DESC NULLS LAST
  )
  SELECT 
    lm.metric_name,
    lm.metric_value,
    CASE
      WHEN lm.metric_name = 'dscr' THEN 1.25
      WHEN lm.metric_name = 'occupancy' THEN 0.85
      WHEN lm.metric_name = 'expense_ratio' THEN 0.50
      ELSE NULL
    END as threshold_value,
    CASE
      WHEN lm.metric_name = 'dscr' AND lm.metric_value < 1.25 THEN 'dscr_below_threshold'
      WHEN lm.metric_name = 'occupancy' AND lm.metric_value < 0.85 THEN 'low_occupancy'
      WHEN lm.metric_name = 'expense_ratio' AND lm.metric_value > 0.50 THEN 'high_expenses'
      ELSE 'no_alert'
    END as alert_type,
    CASE
      WHEN lm.metric_name = 'dscr' AND lm.metric_value < 1.10 THEN 'critical'
      WHEN lm.metric_name = 'dscr' AND lm.metric_value < 1.25 THEN 'warning'
      WHEN lm.metric_name = 'occupancy' AND lm.metric_value < 0.75 THEN 'critical'
      WHEN lm.metric_name = 'occupancy' AND lm.metric_value < 0.85 THEN 'warning'
      WHEN lm.metric_name = 'expense_ratio' AND lm.metric_value > 0.60 THEN 'critical'
      WHEN lm.metric_name = 'expense_ratio' AND lm.metric_value > 0.50 THEN 'warning'
      ELSE 'normal'
    END as severity
  FROM latest_metrics lm
  WHERE lm.metric_name IN ('dscr', 'occupancy', 'expense_ratio');
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Comments for Documentation
-- ============================================================================

COMMENT ON TABLE extracted_metrics IS 'Individual financial metrics extracted from documents with validation and anomaly detection';

COMMENT ON COLUMN extracted_metrics.id IS 'Unique identifier (UUID) for the metric';
COMMENT ON COLUMN extracted_metrics.document_id IS 'Foreign key to financial_documents table';
COMMENT ON COLUMN extracted_metrics.property_id IS 'Foreign key to properties table';
COMMENT ON COLUMN extracted_metrics.metric_name IS 'Name of the metric (e.g., gross_revenue, noi, dscr, occupancy)';
COMMENT ON COLUMN extracted_metrics.metric_category IS 'Category: financial, occupancy, operational, expense, revenue, debt_service, valuation, ratio';
COMMENT ON COLUMN extracted_metrics.metric_value IS 'Numeric value of the metric';
COMMENT ON COLUMN extracted_metrics.metric_unit IS 'Unit: $, %, count, sqft, ratio, days, months, years, units';
COMMENT ON COLUMN extracted_metrics.metric_date IS 'Date the metric is for (e.g., Q3 2024)';
COMMENT ON COLUMN extracted_metrics.confidence_score IS 'Extraction confidence (0.00 to 1.00) - higher is more reliable';
COMMENT ON COLUMN extracted_metrics.extraction_method IS 'How extracted: table_structured, ocr_clear, ocr_fuzzy, pattern_match, ml_inference, manual_entry, api_import, calculated';
COMMENT ON COLUMN extracted_metrics.is_validated IS 'Whether manually reviewed by analyst';
COMMENT ON COLUMN extracted_metrics.validated_by IS 'UUID of user who validated';
COMMENT ON COLUMN extracted_metrics.validated_at IS 'When validated';
COMMENT ON COLUMN extracted_metrics.validation_notes IS 'Notes from manual validation';
COMMENT ON COLUMN extracted_metrics.is_anomaly IS 'Flagged as anomaly by statistical analysis';
COMMENT ON COLUMN extracted_metrics.anomaly_type IS 'Type: z_score, cusum, trend_shift, iqr_outlier, manual_flag, threshold_breach';
COMMENT ON COLUMN extracted_metrics.anomaly_score IS 'Z-score or similar anomaly metric';
COMMENT ON COLUMN extracted_metrics.source_page_number IS 'Which page in document';
COMMENT ON COLUMN extracted_metrics.source_table_number IS 'Which table on page';
COMMENT ON COLUMN extracted_metrics.source_text_snippet IS 'Original text extracted from document';
COMMENT ON COLUMN extracted_metrics.created_at IS 'Timestamp when record was created';
COMMENT ON COLUMN extracted_metrics.updated_at IS 'Timestamp when record was last updated (auto-updated)';
COMMENT ON COLUMN extracted_metrics.created_by IS 'UUID of user who created the record';

-- ============================================================================
-- Success Message
-- ============================================================================

DO $$
BEGIN
  RAISE NOTICE '✅ Extracted Metrics table created successfully';
  RAISE NOTICE '✅ Indexes created (11 indexes)';
  RAISE NOTICE '✅ Constraints added (9 constraints)';
  RAISE NOTICE '✅ Trigger created (updated_at)';
  RAISE NOTICE '✅ Functions created (4 functions)';
  RAISE NOTICE '✅ Comments added for documentation';
  RAISE NOTICE '';
  RAISE NOTICE '📊 Table: extracted_metrics';
  RAISE NOTICE '📊 Columns: 23';
  RAISE NOTICE '📊 Indexes: 11';
  RAISE NOTICE '📊 Constraints: 9';
  RAISE NOTICE '📊 Trigger: 1';
  RAISE NOTICE '📊 Functions: 4';
  RAISE NOTICE '';
  RAISE NOTICE '🔗 Foreign Keys:';
  RAISE NOTICE '   • document_id → financial_documents(id) ON DELETE CASCADE';
  RAISE NOTICE '   • property_id → properties(id) ON DELETE CASCADE';
  RAISE NOTICE '';
  RAISE NOTICE '⚡ Special Functions:';
  RAISE NOTICE '   • get_latest_metrics(property_id) - Latest value for each metric';
  RAISE NOTICE '   • detect_metric_anomalies(property_id, metric_name, z_threshold) - Z-score anomaly detection';
  RAISE NOTICE '   • get_metric_timeseries(property_id, metric_name, start_date, end_date) - Time series data';
  RAISE NOTICE '   • check_metric_alerts(property_id) - Alert threshold checks';
  RAISE NOTICE '';
  RAISE NOTICE '📈 Use Cases:';
  RAISE NOTICE '   1. KPI cards (latest metric for each property)';
  RAISE NOTICE '   2. Anomaly detection (z-score, CUSUM analysis)';
  RAISE NOTICE '   3. Alert generation (DSCR < 1.25, occupancy < 0.85)';
  RAISE NOTICE '   4. Exit strategy analysis (IRR calculations)';
  RAISE NOTICE '';
  RAISE NOTICE '🔍 Sample query:';
  RAISE NOTICE '   SELECT * FROM get_latest_metrics(''property-uuid'');';
  RAISE NOTICE '';
  RAISE NOTICE '🔍 Detect anomalies:';
  RAISE NOTICE '   SELECT * FROM detect_metric_anomalies(''prop-id'', ''noi'', 3.0);';
END $$;

















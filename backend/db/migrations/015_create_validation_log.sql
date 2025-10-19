-- ============================================================================
-- REIMS Data Validation Log Table Migration
-- Version: 015
-- Description: Create table for logging data validation results
-- Author: REIMS Development Team
-- Date: October 19, 2025
-- ============================================================================

-- Drop table if exists (for development/testing)
-- Uncomment next line if you want to recreate the table
-- DROP TABLE IF EXISTS data_validation_log CASCADE;

-- ============================================================================
-- Main Validation Log Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS data_validation_log (
  -- Primary Key
  id TEXT PRIMARY KEY,
  
  -- References
  document_id TEXT NOT NULL,
  property_id INTEGER,
  
  -- Validation Details
  validation_type TEXT NOT NULL, -- 'rent_roll', 'financial_statement', 'lease_document'
  expected_count INTEGER,
  actual_count INTEGER,
  match_status TEXT NOT NULL, -- 'pass', 'warning', 'fail'
  
  -- Discrepancies (JSON)
  discrepancies TEXT, -- JSON array of discrepancy objects
  
  -- Metadata
  validation_notes TEXT,
  validated_by TEXT,
  
  -- Audit Trail
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- Performance Indexes
-- ============================================================================

-- Document ID index (for looking up validation by document)
CREATE INDEX IF NOT EXISTS idx_validation_log_document_id 
  ON data_validation_log(document_id);

-- Property ID index (for looking up validation by property)
CREATE INDEX IF NOT EXISTS idx_validation_log_property_id 
  ON data_validation_log(property_id);

-- Validation type index (for filtering by type)
CREATE INDEX IF NOT EXISTS idx_validation_log_type 
  ON data_validation_log(validation_type);

-- Match status index (for filtering by status)
CREATE INDEX IF NOT EXISTS idx_validation_log_status 
  ON data_validation_log(match_status);

-- Created date index (for sorting by newest)
CREATE INDEX IF NOT EXISTS idx_validation_log_created_at 
  ON data_validation_log(created_at DESC);

-- ============================================================================
-- Comments for Documentation
-- ============================================================================

-- SQLite doesn't support COMMENT ON, but here are the field descriptions:

-- id: Unique identifier (UUID) for the validation log entry
-- document_id: ID of the document that was validated
-- property_id: ID of the property the document belongs to
-- validation_type: Type of validation performed
-- expected_count: Expected number of records (e.g., lease count from source)
-- actual_count: Actual number of records extracted
-- match_status: Overall validation status (pass/warning/fail)
-- discrepancies: JSON array of specific discrepancies found
-- validation_notes: Additional notes about the validation
-- validated_by: User or system that performed validation
-- created_at: Timestamp when validation was performed

-- ============================================================================
-- Verification Query
-- ============================================================================

-- Run this to verify the table was created successfully:
-- SELECT name, sql FROM sqlite_master WHERE type='table' AND name='data_validation_log';

-- ============================================================================
-- Sample Query
-- ============================================================================

-- Get recent validation results:
-- SELECT 
--     document_id,
--     validation_type,
--     match_status,
--     expected_count,
--     actual_count,
--     created_at
-- FROM data_validation_log
-- ORDER BY created_at DESC
-- LIMIT 10;

-- ============================================================================
-- End of Migration
-- ============================================================================


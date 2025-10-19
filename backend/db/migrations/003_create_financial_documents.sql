-- ============================================================================
-- REIMS Financial Documents Table Migration
-- Version: 003
-- Description: Create financial_documents table for document tracking & processing
-- Author: REIMS Development Team
-- Date: October 12, 2025
-- ============================================================================

-- Drop table if exists (for development/testing)
-- Uncomment next line if you want to recreate the table
-- DROP TABLE IF EXISTS financial_documents CASCADE;

-- ============================================================================
-- Main Financial Documents Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS financial_documents (
  -- Primary Key
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Foreign Key to Properties
  property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
  
  -- ========================================================================
  -- File Information
  -- ========================================================================
  file_name VARCHAR(255) NOT NULL,
  file_path TEXT NOT NULL, -- Path in MinIO: properties/prop-001/doc-id_name.pdf
  file_size_bytes INTEGER,
  file_hash VARCHAR(64), -- SHA-256 hash for deduplication
  mime_type VARCHAR(50), -- application/pdf, application/vnd.ms-excel, text/csv
  
  -- ========================================================================
  -- Document Classification
  -- ========================================================================
  document_type VARCHAR(50) NOT NULL, -- 'lease', 'offering_memo', 'financial_stmt', etc.
  document_name VARCHAR(255),
  
  -- ========================================================================
  -- Processing Status
  -- ========================================================================
  status VARCHAR(20) NOT NULL DEFAULT 'queued', -- 'queued', 'processing', 'processed', 'failed', 'reviewed'
  processing_status_detail VARCHAR(255), -- "Extracting tables...", "OCR in progress..."
  
  -- ========================================================================
  -- Dates
  -- ========================================================================
  upload_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  document_date DATE, -- Date of the document itself (not upload date)
  processing_start_date TIMESTAMP,
  processing_end_date TIMESTAMP,
  processing_duration_seconds DECIMAL(10, 2), -- How long it took to process
  
  -- ========================================================================
  -- Extracted Data Metadata
  -- ========================================================================
  extracted_metrics_count INTEGER DEFAULT 0,
  total_tables_found INTEGER,
  total_text_pages INTEGER,
  ocr_required BOOLEAN DEFAULT false,
  
  -- ========================================================================
  -- Quality/Confidence
  -- ========================================================================
  avg_extraction_confidence DECIMAL(3, 2), -- Average confidence (0.00 to 1.00)
  
  -- ========================================================================
  -- Error Handling
  -- ========================================================================
  error_message TEXT,
  error_code VARCHAR(50),
  processing_attempts INTEGER DEFAULT 0,
  last_error_at TIMESTAMP,
  
  -- ========================================================================
  -- AI Processing
  -- ========================================================================
  ai_summary_generated BOOLEAN DEFAULT false,
  ai_summary_confidence DECIMAL(3, 2),
  
  -- ========================================================================
  -- Audit & Security
  -- ========================================================================
  created_by UUID,
  reviewed_by UUID,
  reviewed_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- Performance Indexes
-- ============================================================================

-- Property ID index (for filtering documents by property)
CREATE INDEX IF NOT EXISTS idx_docs_property_id 
  ON financial_documents(property_id);

-- Status index (for filtering by processing status)
CREATE INDEX IF NOT EXISTS idx_docs_status 
  ON financial_documents(status);

-- Composite index for property + status queries
CREATE INDEX IF NOT EXISTS idx_docs_property_status 
  ON financial_documents(property_id, status);

-- Upload date index (for sorting by newest)
CREATE INDEX IF NOT EXISTS idx_docs_upload_date 
  ON financial_documents(upload_date DESC);

-- Document type index (for filtering by document type)
CREATE INDEX IF NOT EXISTS idx_docs_document_type 
  ON financial_documents(document_type);

-- File hash index (for deduplication)
CREATE INDEX IF NOT EXISTS idx_docs_file_hash 
  ON financial_documents(file_hash) 
  WHERE file_hash IS NOT NULL;

-- Document date index (for date-based filtering)
CREATE INDEX IF NOT EXISTS idx_docs_document_date 
  ON financial_documents(document_date) 
  WHERE document_date IS NOT NULL;

-- Created date index
CREATE INDEX IF NOT EXISTS idx_docs_created_at 
  ON financial_documents(created_at DESC);

-- Processing attempts index (for retry logic)
CREATE INDEX IF NOT EXISTS idx_docs_processing_attempts 
  ON financial_documents(processing_attempts) 
  WHERE status = 'failed';

-- ============================================================================
-- Constraints
-- ============================================================================

-- Status must be valid
ALTER TABLE financial_documents 
  DROP CONSTRAINT IF EXISTS chk_status_valid;
ALTER TABLE financial_documents 
  ADD CONSTRAINT chk_status_valid 
  CHECK (status IN ('queued', 'processing', 'processed', 'failed', 'reviewed'));

-- Confidence must be between 0 and 1
ALTER TABLE financial_documents 
  DROP CONSTRAINT IF EXISTS chk_confidence;
ALTER TABLE financial_documents 
  ADD CONSTRAINT chk_confidence 
  CHECK (avg_extraction_confidence IS NULL 
    OR (avg_extraction_confidence >= 0 AND avg_extraction_confidence <= 1));

-- AI summary confidence must be between 0 and 1
ALTER TABLE financial_documents 
  DROP CONSTRAINT IF EXISTS chk_ai_confidence;
ALTER TABLE financial_documents 
  ADD CONSTRAINT chk_ai_confidence 
  CHECK (ai_summary_confidence IS NULL 
    OR (ai_summary_confidence >= 0 AND ai_summary_confidence <= 1));

-- File size must be positive
ALTER TABLE financial_documents 
  DROP CONSTRAINT IF EXISTS chk_file_size_positive;
ALTER TABLE financial_documents 
  ADD CONSTRAINT chk_file_size_positive 
  CHECK (file_size_bytes IS NULL OR file_size_bytes > 0);

-- Document type must be valid
ALTER TABLE financial_documents 
  DROP CONSTRAINT IF EXISTS chk_valid_document_type;
ALTER TABLE financial_documents 
  ADD CONSTRAINT chk_valid_document_type 
  CHECK (document_type IN (
    'lease', 'offering_memo', 'financial_stmt', 'appraisal', 
    'insurance', 'tax_return', 'loan_document', 'inspection_report',
    'tenant_estoppel', 'rent_roll', 'operating_statement', 'other'
  ));

-- Processing end date must be after start date
ALTER TABLE financial_documents 
  DROP CONSTRAINT IF EXISTS chk_processing_dates;
ALTER TABLE financial_documents 
  ADD CONSTRAINT chk_processing_dates 
  CHECK (processing_start_date IS NULL OR processing_end_date IS NULL 
    OR processing_end_date >= processing_start_date);

-- Processing attempts must be non-negative
ALTER TABLE financial_documents 
  DROP CONSTRAINT IF EXISTS chk_processing_attempts_positive;
ALTER TABLE financial_documents 
  ADD CONSTRAINT chk_processing_attempts_positive 
  CHECK (processing_attempts >= 0);

-- Extracted metrics count must be non-negative
ALTER TABLE financial_documents 
  DROP CONSTRAINT IF EXISTS chk_metrics_count_positive;
ALTER TABLE financial_documents 
  ADD CONSTRAINT chk_metrics_count_positive 
  CHECK (extracted_metrics_count >= 0);

-- Document date should not be in the far future
ALTER TABLE financial_documents 
  DROP CONSTRAINT IF EXISTS chk_document_date_reasonable;
ALTER TABLE financial_documents 
  ADD CONSTRAINT chk_document_date_reasonable 
  CHECK (document_date IS NULL OR document_date <= CURRENT_DATE + INTERVAL '1 year');

-- ============================================================================
-- Trigger for Updated Timestamp
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_financial_documents_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop trigger if exists
DROP TRIGGER IF EXISTS trg_financial_documents_updated_at ON financial_documents;

-- Create trigger
CREATE TRIGGER trg_financial_documents_updated_at
  BEFORE UPDATE ON financial_documents
  FOR EACH ROW
  EXECUTE FUNCTION update_financial_documents_updated_at();

-- ============================================================================
-- Trigger to Auto-Calculate Processing Duration
-- ============================================================================

CREATE OR REPLACE FUNCTION calculate_processing_duration()
RETURNS TRIGGER AS $$
BEGIN
  -- If processing_end_date is being set and start_date exists
  IF NEW.processing_end_date IS NOT NULL AND NEW.processing_start_date IS NOT NULL THEN
    NEW.processing_duration_seconds := EXTRACT(EPOCH FROM (NEW.processing_end_date - NEW.processing_start_date));
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop trigger if exists
DROP TRIGGER IF EXISTS trg_calculate_processing_duration ON financial_documents;

-- Create trigger
CREATE TRIGGER trg_calculate_processing_duration
  BEFORE INSERT OR UPDATE ON financial_documents
  FOR EACH ROW
  EXECUTE FUNCTION calculate_processing_duration();

-- ============================================================================
-- Function to Check for Duplicate Documents
-- ============================================================================

CREATE OR REPLACE FUNCTION find_duplicate_documents(p_file_hash VARCHAR(64))
RETURNS TABLE (
  doc_id UUID,
  property_id UUID,
  file_name VARCHAR(255),
  upload_date TIMESTAMP
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    id,
    financial_documents.property_id,
    financial_documents.file_name,
    financial_documents.upload_date
  FROM financial_documents
  WHERE file_hash = p_file_hash
  ORDER BY upload_date DESC;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Function to Get Document Processing Statistics
-- ============================================================================

CREATE OR REPLACE FUNCTION get_document_processing_stats(p_property_id UUID DEFAULT NULL)
RETURNS TABLE (
  status VARCHAR(20),
  document_count INTEGER,
  avg_duration_seconds DECIMAL(10, 2),
  total_size_mb DECIMAL(10, 2)
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    financial_documents.status,
    COUNT(*)::INTEGER as document_count,
    ROUND(AVG(processing_duration_seconds), 2) as avg_duration_seconds,
    ROUND(SUM(file_size_bytes) / 1024.0 / 1024.0, 2) as total_size_mb
  FROM financial_documents
  WHERE p_property_id IS NULL OR property_id = p_property_id
  GROUP BY financial_documents.status
  ORDER BY document_count DESC;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Comments for Documentation
-- ============================================================================

COMMENT ON TABLE financial_documents IS 'Documents uploaded for properties (leases, financials, appraisals, etc.) with processing status tracking';

COMMENT ON COLUMN financial_documents.id IS 'Unique identifier (UUID) for the document';
COMMENT ON COLUMN financial_documents.property_id IS 'Foreign key to properties table';
COMMENT ON COLUMN financial_documents.file_name IS 'Original filename when uploaded';
COMMENT ON COLUMN financial_documents.file_path IS 'Path in MinIO storage (e.g., properties/{propertyId}/{documentId}_{fileName})';
COMMENT ON COLUMN financial_documents.file_size_bytes IS 'File size in bytes';
COMMENT ON COLUMN financial_documents.file_hash IS 'SHA-256 hash for deduplication';
COMMENT ON COLUMN financial_documents.mime_type IS 'MIME type (e.g., application/pdf, application/vnd.ms-excel, text/csv)';
COMMENT ON COLUMN financial_documents.document_type IS 'Type: lease, offering_memo, financial_stmt, appraisal, insurance, tax_return, etc.';
COMMENT ON COLUMN financial_documents.document_name IS 'Optional descriptive name for the document';
COMMENT ON COLUMN financial_documents.status IS 'Processing status: queued, processing, processed, failed, reviewed';
COMMENT ON COLUMN financial_documents.processing_status_detail IS 'Detailed status message (e.g., "Extracting tables...", "OCR in progress...")';
COMMENT ON COLUMN financial_documents.upload_date IS 'When the document was uploaded';
COMMENT ON COLUMN financial_documents.document_date IS 'Date of the document itself (not upload date)';
COMMENT ON COLUMN financial_documents.processing_start_date IS 'When processing started';
COMMENT ON COLUMN financial_documents.processing_end_date IS 'When processing completed';
COMMENT ON COLUMN financial_documents.processing_duration_seconds IS 'How long processing took (auto-calculated)';
COMMENT ON COLUMN financial_documents.extracted_metrics_count IS 'Number of metrics extracted from this document';
COMMENT ON COLUMN financial_documents.total_tables_found IS 'Number of tables detected in the document';
COMMENT ON COLUMN financial_documents.total_text_pages IS 'Number of pages with extractable text';
COMMENT ON COLUMN financial_documents.ocr_required IS 'Whether OCR was needed (scanned document)';
COMMENT ON COLUMN financial_documents.avg_extraction_confidence IS 'Average confidence of extracted metrics (0.00 to 1.00)';
COMMENT ON COLUMN financial_documents.error_message IS 'Error message if processing failed';
COMMENT ON COLUMN financial_documents.error_code IS 'Error code for categorizing failures';
COMMENT ON COLUMN financial_documents.processing_attempts IS 'Number of times processing was attempted';
COMMENT ON COLUMN financial_documents.last_error_at IS 'Timestamp of last error';
COMMENT ON COLUMN financial_documents.ai_summary_generated IS 'Whether AI summary was generated';
COMMENT ON COLUMN financial_documents.ai_summary_confidence IS 'Confidence of AI-generated summary';
COMMENT ON COLUMN financial_documents.created_by IS 'UUID of user who uploaded the document';
COMMENT ON COLUMN financial_documents.reviewed_by IS 'UUID of user who reviewed the document';
COMMENT ON COLUMN financial_documents.reviewed_at IS 'When the document was reviewed';
COMMENT ON COLUMN financial_documents.created_at IS 'Timestamp when record was created';
COMMENT ON COLUMN financial_documents.updated_at IS 'Timestamp when record was last updated (auto-updated)';

-- ============================================================================
-- Success Message
-- ============================================================================

DO $$
BEGIN
  RAISE NOTICE '✅ Financial Documents table created successfully';
  RAISE NOTICE '✅ Indexes created (9 indexes)';
  RAISE NOTICE '✅ Constraints added (9 constraints)';
  RAISE NOTICE '✅ Triggers created (updated_at, calculate_processing_duration)';
  RAISE NOTICE '✅ Functions created (find_duplicate_documents, get_document_processing_stats)';
  RAISE NOTICE '✅ Comments added for documentation';
  RAISE NOTICE '';
  RAISE NOTICE '📊 Table: financial_documents';
  RAISE NOTICE '📊 Columns: 33';
  RAISE NOTICE '📊 Indexes: 9';
  RAISE NOTICE '📊 Constraints: 9';
  RAISE NOTICE '📊 Triggers: 2';
  RAISE NOTICE '📊 Functions: 2';
  RAISE NOTICE '';
  RAISE NOTICE '🔗 Foreign Key: property_id → properties(id) ON DELETE CASCADE';
  RAISE NOTICE '🔍 Deduplication: file_hash (SHA-256)';
  RAISE NOTICE '⚡ Auto-calculate: processing_duration_seconds';
  RAISE NOTICE '';
  RAISE NOTICE '📁 Status Workflow: queued → processing → processed/failed → reviewed';
  RAISE NOTICE '';
  RAISE NOTICE '🔍 Sample query:';
  RAISE NOTICE '   SELECT file_name, document_type, status, processing_duration_seconds';
  RAISE NOTICE '   FROM financial_documents WHERE property_id = ''your-property-id'';';
  RAISE NOTICE '';
  RAISE NOTICE '🔍 Check duplicates:';
  RAISE NOTICE '   SELECT * FROM find_duplicate_documents(''file-hash-here'');';
  RAISE NOTICE '';
  RAISE NOTICE '🔍 Get stats:';
  RAISE NOTICE '   SELECT * FROM get_document_processing_stats();';
END $$;

















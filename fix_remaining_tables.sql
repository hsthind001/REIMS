-- Fix processing_jobs and create extracted_data table
BEGIN;

-- Add job_id column to processing_jobs if it doesn't exist
ALTER TABLE processing_jobs 
    ADD COLUMN IF NOT EXISTS job_id VARCHAR(255) UNIQUE;

-- Update job_id for existing records
UPDATE processing_jobs 
SET job_id = id::text 
WHERE job_id IS NULL;

-- Create index on job_id
CREATE INDEX IF NOT EXISTS idx_processing_jobs_job_id ON processing_jobs(job_id);

-- Create extracted_data table if it doesn't exist
CREATE TABLE IF NOT EXISTS extracted_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id VARCHAR(255) NOT NULL,
    data_type VARCHAR(50) NOT NULL,
    extracted_content JSONB NOT NULL,
    analysis_results JSONB,
    property_indicators JSONB,
    extraction_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    row_count INTEGER,
    column_count INTEGER,
    sheet_count INTEGER,
    page_count INTEGER,
    word_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for extracted_data
CREATE INDEX IF NOT EXISTS idx_extracted_data_document_id ON extracted_data(document_id);
CREATE INDEX IF NOT EXISTS idx_extracted_data_data_type ON extracted_data(data_type);

COMMIT;

-- Verify changes
SELECT 'processing_jobs columns:' as info;
\d processing_jobs

SELECT 'extracted_data table:' as info;
\d extracted_data


-- Fix documents table schema to match backend expectations
-- This adds the missing columns needed for file uploads

BEGIN;

-- Add missing columns to documents table
ALTER TABLE documents 
    ADD COLUMN IF NOT EXISTS document_id VARCHAR(255) UNIQUE,
    ADD COLUMN IF NOT EXISTS original_filename VARCHAR(500),
    ADD COLUMN IF NOT EXISTS stored_filename VARCHAR(500),
    ADD COLUMN IF NOT EXISTS property_id VARCHAR(255),
    ADD COLUMN IF NOT EXISTS upload_timestamp TIMESTAMP,
    ADD COLUMN IF NOT EXISTS minio_bucket VARCHAR(255),
    ADD COLUMN IF NOT EXISTS minio_object_name VARCHAR(1000),
    ADD COLUMN IF NOT EXISTS minio_url VARCHAR(2000),
    ADD COLUMN IF NOT EXISTS storage_type VARCHAR(50) DEFAULT 'local',
    ADD COLUMN IF NOT EXISTS minio_upload_timestamp TIMESTAMP;

-- Create index on document_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_documents_document_id ON documents(document_id);

-- Create index on property_id for faster filtering
CREATE INDEX IF NOT EXISTS idx_documents_property_id ON documents(property_id);

-- Update existing records to populate new fields (if any exist)
UPDATE documents 
SET 
    document_id = COALESCE(document_id, id::text),
    original_filename = COALESCE(original_filename, filename),
    stored_filename = COALESCE(stored_filename, filename),
    upload_timestamp = COALESCE(upload_timestamp, upload_date)
WHERE document_id IS NULL;

COMMIT;

-- Verify the changes
\d documents


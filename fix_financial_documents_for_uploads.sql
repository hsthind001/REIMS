-- Add columns to financial_documents table to support file uploads
BEGIN;

ALTER TABLE financial_documents 
    ADD COLUMN IF NOT EXISTS file_name VARCHAR(500),
    ADD COLUMN IF NOT EXISTS file_path VARCHAR(2000),
    ADD COLUMN IF NOT EXISTS document_type VARCHAR(100),
    ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'queued',
    ADD COLUMN IF NOT EXISTS upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ADD COLUMN IF NOT EXISTS processing_date TIMESTAMP,
    ADD COLUMN IF NOT EXISTS error_message TEXT;

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_financial_documents_status ON financial_documents(status);
CREATE INDEX IF NOT EXISTS idx_financial_documents_document_type ON financial_documents(document_type);
CREATE INDEX IF NOT EXISTS idx_financial_documents_upload_date ON financial_documents(upload_date DESC);

COMMIT;

-- Verify the changes
\d financial_documents


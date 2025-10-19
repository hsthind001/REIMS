-- Migration 007: Create Audit Log Table
-- Purpose: Complete traceability for compliance and debugging
-- Required by: BR-007 (export audit bundles for regulators)
-- Date: 2025-10-12

-- ============================================================================
-- AUDIT_LOG TABLE: Complete traceability for all system actions
-- ============================================================================

CREATE TABLE IF NOT EXISTS audit_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Action Information
  action VARCHAR(100) NOT NULL, -- 'DOCUMENT_UPLOAD', 'ALERT_CREATED', 'APPROVAL_DECISION'
  action_category VARCHAR(50), -- 'document', 'alert', 'approval', 'export', 'data_access'
  
  -- Business Requirement Linkage
  br_id VARCHAR(20), -- 'BR-001', 'BR-003', 'BR-007'
  br_description VARCHAR(255),
  
  -- Subject References
  property_id UUID REFERENCES properties(id) ON DELETE SET NULL,
  document_id UUID REFERENCES financial_documents(id) ON DELETE SET NULL,
  alert_id UUID REFERENCES committee_alerts(id) ON DELETE SET NULL,
  
  -- User Information
  user_id UUID,
  user_email VARCHAR(255),
  user_role VARCHAR(50), -- 'supervisor', 'analyst', 'viewer'
  ip_address INET,
  user_agent TEXT,
  
  -- Change Details
  old_values JSONB, -- What changed FROM
  new_values JSONB, -- What changed TO
  details JSONB, -- Additional context
  
  -- Status
  success BOOLEAN DEFAULT true,
  error_message TEXT,
  
  -- Session Information
  session_id VARCHAR(100),
  request_id VARCHAR(100), -- Correlate related requests
  
  -- Timestamp
  timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEXES: Optimized for compliance audits and security reviews
-- ============================================================================

-- Primary temporal index (most common query pattern)
CREATE INDEX idx_audit_timestamp ON audit_log(timestamp DESC);

-- User activity tracking
CREATE INDEX idx_audit_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_user_timestamp ON audit_log(user_id, timestamp DESC);

-- Action tracking
CREATE INDEX idx_audit_action ON audit_log(action);

-- Business requirement tracking
CREATE INDEX idx_audit_br_id ON audit_log(br_id);

-- Entity-specific audits
CREATE INDEX idx_audit_property_id ON audit_log(property_id);
CREATE INDEX idx_audit_property_timestamp ON audit_log(property_id, timestamp DESC);
CREATE INDEX idx_audit_document_id ON audit_log(document_id);

-- ============================================================================
-- TABLE COMMENTS: Documentation for database administrators
-- ============================================================================

COMMENT ON TABLE audit_log IS 'Immutable audit trail for all system actions. Required for BR-007 compliance exports. Never delete records.';

COMMENT ON COLUMN audit_log.action IS 'Type of action performed (e.g., DOCUMENT_UPLOAD, ALERT_CREATED, APPROVAL_DECISION)';
COMMENT ON COLUMN audit_log.action_category IS 'High-level category: document, alert, approval, export, data_access';
COMMENT ON COLUMN audit_log.br_id IS 'Business Requirement ID this action supports (BR-001 through BR-012)';
COMMENT ON COLUMN audit_log.br_description IS 'Human-readable description of the business requirement';

COMMENT ON COLUMN audit_log.property_id IS 'Property affected by this action (if applicable)';
COMMENT ON COLUMN audit_log.document_id IS 'Document affected by this action (if applicable)';
COMMENT ON COLUMN audit_log.alert_id IS 'Alert affected by this action (if applicable)';

COMMENT ON COLUMN audit_log.user_id IS 'UUID of user who performed the action';
COMMENT ON COLUMN audit_log.user_email IS 'Email of user who performed the action';
COMMENT ON COLUMN audit_log.user_role IS 'Role at time of action: supervisor, analyst, viewer';
COMMENT ON COLUMN audit_log.ip_address IS 'IP address of the request';
COMMENT ON COLUMN audit_log.user_agent IS 'Browser/client user agent string';

COMMENT ON COLUMN audit_log.old_values IS 'JSON snapshot of values BEFORE the change (enables rollback)';
COMMENT ON COLUMN audit_log.new_values IS 'JSON snapshot of values AFTER the change';
COMMENT ON COLUMN audit_log.details IS 'Additional context about the action';

COMMENT ON COLUMN audit_log.success IS 'Whether the action completed successfully';
COMMENT ON COLUMN audit_log.error_message IS 'Error details if success=false';

COMMENT ON COLUMN audit_log.session_id IS 'Session identifier for grouping related actions';
COMMENT ON COLUMN audit_log.request_id IS 'Unique request ID for correlating distributed operations';

COMMENT ON COLUMN audit_log.timestamp IS 'When the action occurred (UTC)';

-- ============================================================================
-- OPTIONAL: Table partitioning for high-volume deployments
-- ============================================================================

-- Uncomment and customize for deployments with > 1M audit records
-- This example shows monthly partitioning
-- 
-- CREATE TABLE audit_log_2025_10 PARTITION OF audit_log
-- FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');
-- 
-- CREATE TABLE audit_log_2025_11 PARTITION OF audit_log
-- FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');
-- 
-- Note: Requires converting audit_log to a partitioned table first:
-- CREATE TABLE audit_log (...) PARTITION BY RANGE (timestamp);

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Verify table creation
DO $$
BEGIN
  IF EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name = 'audit_log'
  ) THEN
    RAISE NOTICE 'audit_log table created successfully';
  ELSE
    RAISE EXCEPTION 'audit_log table creation failed';
  END IF;
END $$;

-- ============================================================================
-- USAGE EXAMPLES (for developers)
-- ============================================================================

-- Example 1: Log a document upload
-- INSERT INTO audit_log (
--   action, action_category, br_id, br_description,
--   property_id, document_id, user_id, user_email, user_role,
--   new_values, details, session_id, request_id
-- ) VALUES (
--   'DOCUMENT_UPLOAD', 'document', 'BR-001', 'AI-powered document processing',
--   '123e4567-e89b-12d3-a456-426614174000',
--   '789e4567-e89b-12d3-a456-426614174999',
--   'user-uuid-here', 'analyst@reims.com', 'analyst',
--   '{"filename": "Q3_financials.pdf", "size_bytes": 245678}'::jsonb,
--   '{"upload_source": "web_ui", "processing_mode": "auto"}'::jsonb,
--   'session-abc123', 'req-xyz789'
-- );

-- Example 2: Log an approval decision
-- INSERT INTO audit_log (
--   action, action_category, br_id, br_description,
--   alert_id, user_id, user_email, user_role,
--   old_values, new_values, details
-- ) VALUES (
--   'APPROVAL_DECISION', 'approval', 'BR-003', 'Committee approval workflow',
--   'alert-uuid-here', 'supervisor-uuid', 'supervisor@reims.com', 'supervisor',
--   '{"status": "pending", "approved_by": null}'::jsonb,
--   '{"status": "approved", "approved_by": "supervisor@reims.com"}'::jsonb,
--   '{"approval_notes": "Approved after risk review", "decision_time_seconds": 45}'::jsonb
-- );

-- Example 3: Query audit trail for a property
-- SELECT 
--   timestamp, action, user_email, user_role,
--   new_values->>'filename' as document_name,
--   success
-- FROM audit_log
-- WHERE property_id = '123e4567-e89b-12d3-a456-426614174000'
-- ORDER BY timestamp DESC
-- LIMIT 20;

-- Example 4: Generate compliance report for BR-007
-- SELECT 
--   DATE(timestamp) as audit_date,
--   action_category,
--   COUNT(*) as action_count,
--   COUNT(*) FILTER (WHERE success = true) as successful_actions,
--   COUNT(*) FILTER (WHERE success = false) as failed_actions
-- FROM audit_log
-- WHERE timestamp >= CURRENT_DATE - INTERVAL '30 days'
-- GROUP BY DATE(timestamp), action_category
-- ORDER BY audit_date DESC, action_category;


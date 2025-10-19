-- ============================================================================
-- REIMS Committee Alerts Table Migration
-- Version: 005
-- Description: Create committee_alerts table for workflow governance and approval
-- Author: REIMS Development Team
-- Date: October 12, 2025
-- ============================================================================

-- Drop table if exists (for development/testing)
-- Uncomment next line if you want to recreate the table
-- DROP TABLE IF EXISTS committee_alerts CASCADE;

-- ============================================================================
-- Main Committee Alerts Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS committee_alerts (
  -- Primary Key
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Foreign Key
  property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
  
  -- ========================================================================
  -- Alert Type & Severity
  -- ========================================================================
  alert_type VARCHAR(50) NOT NULL, -- 'dscr_low', 'occupancy_low', 'anomaly', 'threshold_breach'
  alert_title VARCHAR(255) NOT NULL,
  alert_description TEXT,
  severity_level VARCHAR(20) NOT NULL DEFAULT 'warning', -- 'critical', 'warning', 'info'
  
  -- ========================================================================
  -- Metric Information
  -- ========================================================================
  metric_name VARCHAR(100), -- Which metric triggered: 'dscr', 'occupancy', 'noi'
  metric_value DECIMAL(18, 2), -- Actual value
  threshold_value DECIMAL(18, 2), -- What threshold was breached
  variance_pct DECIMAL(10, 2), -- How far below threshold (e.g., -5.2%)
  
  -- ========================================================================
  -- Governance
  -- ========================================================================
  committee_responsible VARCHAR(255), -- 'Finance Sub-Committee', 'Occupancy Sub-Committee'
  committee_member_required VARCHAR(20), -- 'supervisor', 'analyst', 'all'
  
  -- ========================================================================
  -- Approval Workflow
  -- ========================================================================
  status VARCHAR(20) NOT NULL DEFAULT 'pending', -- 'pending', 'approved', 'rejected', 'expired'
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by UUID,
  
  approved_at TIMESTAMP,
  approved_by UUID, -- Which user approved
  approval_notes TEXT,
  
  -- ========================================================================
  -- Decision Information
  -- ========================================================================
  decision_reason VARCHAR(255), -- Why approved/rejected
  requires_action BOOLEAN DEFAULT true, -- Does this require action?
  action_item_assigned_to UUID,
  action_due_date DATE,
  
  -- ========================================================================
  -- Resolution
  -- ========================================================================
  resolved_at TIMESTAMP,
  resolution_notes TEXT,
  
  -- ========================================================================
  -- Notifications
  -- ========================================================================
  notification_sent_at TIMESTAMP,
  notification_method VARCHAR(50), -- 'email', 'sms', 'in_app'
  
  -- ========================================================================
  -- Expiration (auto-resolve if not acted upon)
  -- ========================================================================
  expires_at TIMESTAMP,
  auto_resolved BOOLEAN DEFAULT false,
  
  -- ========================================================================
  -- Audit
  -- ========================================================================
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- Performance Indexes
-- ============================================================================

-- Property ID index
CREATE INDEX IF NOT EXISTS idx_alerts_property_id 
  ON committee_alerts(property_id);

-- Status index (for filtering pending/approved/rejected)
CREATE INDEX IF NOT EXISTS idx_alerts_status 
  ON committee_alerts(status);

-- Severity index (for filtering critical alerts)
CREATE INDEX IF NOT EXISTS idx_alerts_severity 
  ON committee_alerts(severity_level);

-- Created date index (for sorting by newest)
CREATE INDEX IF NOT EXISTS idx_alerts_created_at 
  ON committee_alerts(created_at DESC);

-- Committee index (for filtering by responsible committee)
CREATE INDEX IF NOT EXISTS idx_alerts_committee 
  ON committee_alerts(committee_responsible);

-- Expiration index (for auto-expiry job)
CREATE INDEX IF NOT EXISTS idx_alerts_expires_at 
  ON committee_alerts(expires_at) 
  WHERE status = 'pending' AND expires_at IS NOT NULL;

-- Composite index for property + status
CREATE INDEX IF NOT EXISTS idx_alerts_property_status 
  ON committee_alerts(property_id, status);

-- Alert type index
CREATE INDEX IF NOT EXISTS idx_alerts_type 
  ON committee_alerts(alert_type);

-- Action assignment index
CREATE INDEX IF NOT EXISTS idx_alerts_assigned_to 
  ON committee_alerts(action_item_assigned_to) 
  WHERE action_item_assigned_to IS NOT NULL;

-- Pending alerts with action required
CREATE INDEX IF NOT EXISTS idx_alerts_action_required 
  ON committee_alerts(status, requires_action) 
  WHERE status = 'pending' AND requires_action = true;

-- ============================================================================
-- Constraints
-- ============================================================================

-- Status must be valid
ALTER TABLE committee_alerts 
  DROP CONSTRAINT IF EXISTS chk_status_valid;
ALTER TABLE committee_alerts 
  ADD CONSTRAINT chk_status_valid 
  CHECK (status IN ('pending', 'approved', 'rejected', 'expired'));

-- Severity must be valid
ALTER TABLE committee_alerts 
  DROP CONSTRAINT IF EXISTS chk_severity_valid;
ALTER TABLE committee_alerts 
  ADD CONSTRAINT chk_severity_valid 
  CHECK (severity_level IN ('critical', 'warning', 'info'));

-- Alert type must be valid
ALTER TABLE committee_alerts 
  DROP CONSTRAINT IF EXISTS chk_alert_type_valid;
ALTER TABLE committee_alerts 
  ADD CONSTRAINT chk_alert_type_valid 
  CHECK (alert_type IN (
    'dscr_low', 'occupancy_low', 'expense_high', 'anomaly', 
    'threshold_breach', 'loan_maturity', 'lease_expiring', 
    'maintenance_required', 'inspection_due', 'custom'
  ));

-- Committee member required must be valid
ALTER TABLE committee_alerts 
  DROP CONSTRAINT IF EXISTS chk_committee_member_valid;
ALTER TABLE committee_alerts 
  ADD CONSTRAINT chk_committee_member_valid 
  CHECK (committee_member_required IS NULL OR committee_member_required IN (
    'supervisor', 'analyst', 'manager', 'all', 'any'
  ));

-- Notification method must be valid
ALTER TABLE committee_alerts 
  DROP CONSTRAINT IF EXISTS chk_notification_method_valid;
ALTER TABLE committee_alerts 
  ADD CONSTRAINT chk_notification_method_valid 
  CHECK (notification_method IS NULL OR notification_method IN (
    'email', 'sms', 'in_app', 'slack', 'teams', 'webhook'
  ));

-- If approved, must have approver and timestamp
ALTER TABLE committee_alerts 
  DROP CONSTRAINT IF EXISTS chk_approval_complete;
ALTER TABLE committee_alerts 
  ADD CONSTRAINT chk_approval_complete 
  CHECK (
    (status != 'approved') OR 
    (status = 'approved' AND approved_by IS NOT NULL AND approved_at IS NOT NULL)
  );

-- If rejected, should have decision reason
ALTER TABLE committee_alerts 
  DROP CONSTRAINT IF EXISTS chk_rejection_reason;
ALTER TABLE committee_alerts 
  ADD CONSTRAINT chk_rejection_reason 
  CHECK (
    (status != 'rejected') OR 
    (status = 'rejected' AND decision_reason IS NOT NULL)
  );

-- Variance percentage should be reasonable
ALTER TABLE committee_alerts 
  DROP CONSTRAINT IF EXISTS chk_variance_reasonable;
ALTER TABLE committee_alerts 
  ADD CONSTRAINT chk_variance_reasonable 
  CHECK (variance_pct IS NULL OR (variance_pct >= -100 AND variance_pct <= 100));

-- Action due date should be in the future when created
ALTER TABLE committee_alerts 
  DROP CONSTRAINT IF EXISTS chk_action_due_future;
ALTER TABLE committee_alerts 
  ADD CONSTRAINT chk_action_due_future 
  CHECK (
    action_due_date IS NULL OR 
    action_due_date >= CURRENT_DATE
  );

-- ============================================================================
-- Trigger for Updated Timestamp
-- ============================================================================

CREATE OR REPLACE FUNCTION update_committee_alerts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_committee_alerts_updated_at ON committee_alerts;

CREATE TRIGGER trg_committee_alerts_updated_at
  BEFORE UPDATE ON committee_alerts
  FOR EACH ROW
  EXECUTE FUNCTION update_committee_alerts_updated_at();

-- ============================================================================
-- Trigger to Auto-Expire Alerts
-- ============================================================================

CREATE OR REPLACE FUNCTION auto_expire_committee_alerts()
RETURNS TRIGGER AS $$
BEGIN
  -- If creating a new alert without expiration, set default to 30 days
  IF NEW.expires_at IS NULL AND NEW.status = 'pending' THEN
    NEW.expires_at := CURRENT_TIMESTAMP + INTERVAL '30 days';
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_auto_expire_alerts ON committee_alerts;

CREATE TRIGGER trg_auto_expire_alerts
  BEFORE INSERT ON committee_alerts
  FOR EACH ROW
  EXECUTE FUNCTION auto_expire_committee_alerts();

-- ============================================================================
-- Function to Expire Old Pending Alerts (Run as scheduled job)
-- ============================================================================

CREATE OR REPLACE FUNCTION expire_pending_alerts()
RETURNS INTEGER AS $$
DECLARE
  expired_count INTEGER;
BEGIN
  UPDATE committee_alerts
  SET 
    status = 'expired',
    auto_resolved = true,
    resolved_at = CURRENT_TIMESTAMP
  WHERE status = 'pending'
    AND expires_at < CURRENT_TIMESTAMP
    AND expires_at IS NOT NULL;
  
  GET DIAGNOSTICS expired_count = ROW_COUNT;
  
  RETURN expired_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Function to Check Active Alerts for Property (BR-003 Workflow Lock)
-- ============================================================================

CREATE OR REPLACE FUNCTION has_active_critical_alerts(p_property_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
  alert_count INTEGER;
BEGIN
  SELECT COUNT(*) INTO alert_count
  FROM committee_alerts
  WHERE property_id = p_property_id
    AND status = 'pending'
    AND severity_level = 'critical'
    AND requires_action = true;
  
  RETURN alert_count > 0;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Function to Get Pending Alerts by Committee
-- ============================================================================

CREATE OR REPLACE FUNCTION get_pending_alerts_by_committee(p_committee VARCHAR(255))
RETURNS TABLE (
  alert_id UUID,
  property_id UUID,
  alert_title VARCHAR(255),
  severity_level VARCHAR(20),
  created_at TIMESTAMP,
  days_pending INTEGER
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    ca.id,
    ca.property_id,
    ca.alert_title,
    ca.severity_level,
    ca.created_at,
    EXTRACT(DAY FROM (CURRENT_TIMESTAMP - ca.created_at))::INTEGER as days_pending
  FROM committee_alerts ca
  WHERE ca.committee_responsible = p_committee
    AND ca.status = 'pending'
  ORDER BY 
    CASE ca.severity_level
      WHEN 'critical' THEN 1
      WHEN 'warning' THEN 2
      WHEN 'info' THEN 3
    END,
    ca.created_at;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Function to Get Alert Summary by Property
-- ============================================================================

CREATE OR REPLACE FUNCTION get_alert_summary(p_property_id UUID)
RETURNS TABLE (
  total_alerts INTEGER,
  pending_alerts INTEGER,
  critical_alerts INTEGER,
  warning_alerts INTEGER,
  approved_alerts INTEGER,
  rejected_alerts INTEGER,
  expired_alerts INTEGER
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    COUNT(*)::INTEGER as total_alerts,
    COUNT(*) FILTER (WHERE status = 'pending')::INTEGER as pending_alerts,
    COUNT(*) FILTER (WHERE severity_level = 'critical' AND status = 'pending')::INTEGER as critical_alerts,
    COUNT(*) FILTER (WHERE severity_level = 'warning' AND status = 'pending')::INTEGER as warning_alerts,
    COUNT(*) FILTER (WHERE status = 'approved')::INTEGER as approved_alerts,
    COUNT(*) FILTER (WHERE status = 'rejected')::INTEGER as rejected_alerts,
    COUNT(*) FILTER (WHERE status = 'expired')::INTEGER as expired_alerts
  FROM committee_alerts
  WHERE property_id = p_property_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Function to Create Alert from Metric Threshold Breach
-- ============================================================================

CREATE OR REPLACE FUNCTION create_threshold_alert(
  p_property_id UUID,
  p_metric_name VARCHAR(100),
  p_metric_value DECIMAL(18, 2),
  p_threshold_value DECIMAL(18, 2),
  p_created_by UUID DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
  new_alert_id UUID;
  alert_severity VARCHAR(20);
  alert_committee VARCHAR(255);
  alert_title VARCHAR(255);
  variance DECIMAL(10, 2);
BEGIN
  -- Calculate variance
  variance := ((p_metric_value - p_threshold_value) / NULLIF(p_threshold_value, 0)) * 100;
  
  -- Determine severity and committee based on metric
  CASE p_metric_name
    WHEN 'dscr' THEN
      IF p_metric_value < 1.10 THEN
        alert_severity := 'critical';
      ELSE
        alert_severity := 'warning';
      END IF;
      alert_committee := 'Finance Sub-Committee';
      alert_title := 'DSCR Below Threshold';
      
    WHEN 'occupancy' THEN
      IF p_metric_value < 0.75 THEN
        alert_severity := 'critical';
      ELSE
        alert_severity := 'warning';
      END IF;
      alert_committee := 'Occupancy Sub-Committee';
      alert_title := 'Low Occupancy Rate';
      
    WHEN 'expense_ratio' THEN
      IF p_metric_value > 0.60 THEN
        alert_severity := 'critical';
      ELSE
        alert_severity := 'warning';
      END IF;
      alert_committee := 'Finance Sub-Committee';
      alert_title := 'High Expense Ratio';
      
    ELSE
      alert_severity := 'warning';
      alert_committee := 'General Committee';
      alert_title := 'Metric Threshold Breach';
  END CASE;
  
  -- Create alert
  INSERT INTO committee_alerts (
    property_id,
    alert_type,
    alert_title,
    alert_description,
    severity_level,
    metric_name,
    metric_value,
    threshold_value,
    variance_pct,
    committee_responsible,
    committee_member_required,
    created_by,
    requires_action
  ) VALUES (
    p_property_id,
    'threshold_breach',
    alert_title,
    format('Metric %s value of %s is below threshold of %s (variance: %s%%)', 
           p_metric_name, p_metric_value, p_threshold_value, ROUND(variance, 2)),
    alert_severity,
    p_metric_name,
    p_metric_value,
    p_threshold_value,
    variance,
    alert_committee,
    CASE WHEN alert_severity = 'critical' THEN 'supervisor' ELSE 'analyst' END,
    p_created_by,
    CASE WHEN alert_severity = 'critical' THEN true ELSE false END
  ) RETURNING id INTO new_alert_id;
  
  RETURN new_alert_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Comments for Documentation
-- ============================================================================

COMMENT ON TABLE committee_alerts IS 'Workflow governance alerts requiring committee approval (BR-003)';

COMMENT ON COLUMN committee_alerts.id IS 'Unique identifier (UUID) for the alert';
COMMENT ON COLUMN committee_alerts.property_id IS 'Foreign key to properties table';
COMMENT ON COLUMN committee_alerts.alert_type IS 'Type: dscr_low, occupancy_low, expense_high, anomaly, threshold_breach, loan_maturity, lease_expiring, etc.';
COMMENT ON COLUMN committee_alerts.alert_title IS 'Short title for the alert';
COMMENT ON COLUMN committee_alerts.alert_description IS 'Detailed description of the alert';
COMMENT ON COLUMN committee_alerts.severity_level IS 'Severity: critical, warning, info';
COMMENT ON COLUMN committee_alerts.metric_name IS 'Which metric triggered the alert (e.g., dscr, occupancy, noi)';
COMMENT ON COLUMN committee_alerts.metric_value IS 'Actual value that triggered the alert';
COMMENT ON COLUMN committee_alerts.threshold_value IS 'Threshold value that was breached';
COMMENT ON COLUMN committee_alerts.variance_pct IS 'How far from threshold (percentage)';
COMMENT ON COLUMN committee_alerts.committee_responsible IS 'Which committee must approve (e.g., Finance Sub-Committee)';
COMMENT ON COLUMN committee_alerts.committee_member_required IS 'Required approver: supervisor, analyst, manager, all, any';
COMMENT ON COLUMN committee_alerts.status IS 'Workflow status: pending, approved, rejected, expired';
COMMENT ON COLUMN committee_alerts.created_at IS 'When alert was created';
COMMENT ON COLUMN committee_alerts.created_by IS 'UUID of user who created the alert';
COMMENT ON COLUMN committee_alerts.approved_at IS 'When alert was approved';
COMMENT ON COLUMN committee_alerts.approved_by IS 'UUID of user who approved';
COMMENT ON COLUMN committee_alerts.approval_notes IS 'Notes from approver';
COMMENT ON COLUMN committee_alerts.decision_reason IS 'Why approved/rejected';
COMMENT ON COLUMN committee_alerts.requires_action IS 'Whether this alert requires action';
COMMENT ON COLUMN committee_alerts.action_item_assigned_to IS 'UUID of user assigned to action item';
COMMENT ON COLUMN committee_alerts.action_due_date IS 'When action must be completed';
COMMENT ON COLUMN committee_alerts.resolved_at IS 'When alert was resolved';
COMMENT ON COLUMN committee_alerts.resolution_notes IS 'How alert was resolved';
COMMENT ON COLUMN committee_alerts.notification_sent_at IS 'When notification was sent';
COMMENT ON COLUMN committee_alerts.notification_method IS 'How notified: email, sms, in_app, slack, teams, webhook';
COMMENT ON COLUMN committee_alerts.expires_at IS 'When alert auto-expires (default 30 days)';
COMMENT ON COLUMN committee_alerts.auto_resolved IS 'Whether alert was auto-resolved due to expiration';
COMMENT ON COLUMN committee_alerts.updated_at IS 'Last update timestamp (auto-updated)';

-- ============================================================================
-- Success Message
-- ============================================================================

DO $$
BEGIN
  RAISE NOTICE '✅ Committee Alerts table created successfully';
  RAISE NOTICE '✅ Indexes created (10 indexes)';
  RAISE NOTICE '✅ Constraints added (9 constraints)';
  RAISE NOTICE '✅ Triggers created (updated_at, auto_expire)';
  RAISE NOTICE '✅ Functions created (6 functions)';
  RAISE NOTICE '✅ Comments added for documentation';
  RAISE NOTICE '';
  RAISE NOTICE '📊 Table: committee_alerts';
  RAISE NOTICE '📊 Columns: 28';
  RAISE NOTICE '📊 Indexes: 10';
  RAISE NOTICE '📊 Constraints: 9';
  RAISE NOTICE '📊 Triggers: 2';
  RAISE NOTICE '📊 Functions: 6';
  RAISE NOTICE '';
  RAISE NOTICE '🔗 Foreign Key: property_id → properties(id) ON DELETE CASCADE';
  RAISE NOTICE '';
  RAISE NOTICE '⚡ Workflow Features:';
  RAISE NOTICE '   • Auto-expire alerts after 30 days (default)';
  RAISE NOTICE '   • Workflow lock for critical alerts (BR-003)';
  RAISE NOTICE '   • Committee-based approval routing';
  RAISE NOTICE '   • Action item assignment & tracking';
  RAISE NOTICE '';
  RAISE NOTICE '🔍 Key Functions:';
  RAISE NOTICE '   • has_active_critical_alerts(property_id) - Check workflow lock';
  RAISE NOTICE '   • expire_pending_alerts() - Auto-expire old alerts';
  RAISE NOTICE '   • get_pending_alerts_by_committee(committee) - Committee dashboard';
  RAISE NOTICE '   • get_alert_summary(property_id) - Alert statistics';
  RAISE NOTICE '   • create_threshold_alert(property_id, metric, value, threshold) - Create alert';
  RAISE NOTICE '';
  RAISE NOTICE '📋 Status Workflow: pending → approved/rejected OR expired';
  RAISE NOTICE '';
  RAISE NOTICE '🔍 Sample query:';
  RAISE NOTICE '   SELECT * FROM get_alert_summary(''property-uuid'');';
  RAISE NOTICE '';
  RAISE NOTICE '🔒 Check workflow lock (BR-003):';
  RAISE NOTICE '   SELECT has_active_critical_alerts(''property-uuid'');';
END $$;

















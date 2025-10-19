-- Migration 006: Create workflow_locks table
-- Purpose: Enforce BR-003 workflow governance by tracking blocked actions when critical alerts exist
-- Created: 2025-10-12

-- =============================================================================
-- TABLE: workflow_locks
-- Description: Prevents specific actions on properties when critical alerts exist
-- Business Rule: BR-003 - Committee approval required before refinance/sale/disposition
-- =============================================================================

CREATE TABLE IF NOT EXISTS workflow_locks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
  alert_id UUID NOT NULL REFERENCES committee_alerts(id) ON DELETE CASCADE,
  
  -- Lock Information
  lock_type VARCHAR(50) NOT NULL, -- 'acquisition_freeze', 'refinance_block', 'sale_hold', 'disposition_block'
  lock_reason VARCHAR(255),
  lock_severity VARCHAR(20) NOT NULL DEFAULT 'critical', -- 'critical', 'warning'
  
  -- Lock Timeline
  locked_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  unlocked_at TIMESTAMP,
  lock_duration_hours INTEGER,
  
  -- Lock Status
  status VARCHAR(20) NOT NULL DEFAULT 'locked', -- 'locked', 'unlocked', 'expired'
  
  -- Who locked/unlocked
  locked_by UUID,
  unlocked_by UUID,
  unlock_reason TEXT,
  
  -- Blocked Actions (what can't be done while locked)
  blocked_actions TEXT[] DEFAULT ARRAY[]::TEXT[], -- ['refinance', 'sell', 'dispose', 'acquisition']
  
  -- Notifications
  lock_notification_sent BOOLEAN DEFAULT false,
  unlock_notification_sent BOOLEAN DEFAULT false,
  
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- INDEXES
-- =============================================================================

CREATE INDEX idx_locks_property_id ON workflow_locks(property_id);
CREATE INDEX idx_locks_alert_id ON workflow_locks(alert_id);
CREATE INDEX idx_locks_status ON workflow_locks(status);
CREATE INDEX idx_locks_locked_at ON workflow_locks(locked_at DESC);
CREATE INDEX idx_locks_property_status ON workflow_locks(property_id, status);
CREATE INDEX idx_locks_lock_type ON workflow_locks(lock_type);
CREATE INDEX idx_locks_severity ON workflow_locks(lock_severity);

-- =============================================================================
-- CONSTRAINTS
-- =============================================================================

ALTER TABLE workflow_locks ADD CONSTRAINT chk_lock_status 
  CHECK (status IN ('locked', 'unlocked', 'expired'));

ALTER TABLE workflow_locks ADD CONSTRAINT chk_lock_severity 
  CHECK (lock_severity IN ('critical', 'warning'));

ALTER TABLE workflow_locks ADD CONSTRAINT chk_lock_type_valid 
  CHECK (lock_type IN ('acquisition_freeze', 'refinance_block', 'sale_hold', 'disposition_block'));

ALTER TABLE workflow_locks ADD CONSTRAINT chk_unlock_after_lock 
  CHECK (unlocked_at IS NULL OR unlocked_at >= locked_at);

-- =============================================================================
-- TRIGGERS
-- =============================================================================

-- Trigger 1: Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_workflow_locks_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_workflow_locks_updated_at
  BEFORE UPDATE ON workflow_locks
  FOR EACH ROW
  EXECUTE FUNCTION update_workflow_locks_timestamp();

-- Trigger 2: Auto-calculate lock_duration_hours when unlocked
CREATE OR REPLACE FUNCTION calculate_lock_duration()
RETURNS TRIGGER AS $$
BEGIN
  -- Only calculate if status changed to 'unlocked' and unlocked_at is set
  IF NEW.status = 'unlocked' AND NEW.unlocked_at IS NOT NULL AND OLD.unlocked_at IS NULL THEN
    NEW.lock_duration_hours = EXTRACT(EPOCH FROM (NEW.unlocked_at - NEW.locked_at)) / 3600;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_calculate_lock_duration
  BEFORE UPDATE ON workflow_locks
  FOR EACH ROW
  WHEN (NEW.status = 'unlocked' AND NEW.unlocked_at IS NOT NULL)
  EXECUTE FUNCTION calculate_lock_duration();

-- Trigger 3: Sync property has_active_alerts flag
CREATE OR REPLACE FUNCTION sync_property_workflow_lock()
RETURNS TRIGGER AS $$
BEGIN
  -- Update property's has_active_alerts flag based on active locks
  UPDATE properties
  SET has_active_alerts = EXISTS (
    SELECT 1 FROM workflow_locks
    WHERE property_id = COALESCE(NEW.property_id, OLD.property_id)
    AND status = 'locked'
  )
  WHERE id = COALESCE(NEW.property_id, OLD.property_id);
  
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_sync_property_workflow_lock_insert
  AFTER INSERT ON workflow_locks
  FOR EACH ROW
  EXECUTE FUNCTION sync_property_workflow_lock();

CREATE TRIGGER trg_sync_property_workflow_lock_update
  AFTER UPDATE ON workflow_locks
  FOR EACH ROW
  WHEN (OLD.status IS DISTINCT FROM NEW.status)
  EXECUTE FUNCTION sync_property_workflow_lock();

-- =============================================================================
-- BUSINESS LOGIC FUNCTIONS
-- =============================================================================

-- Function 1: Check if specific action is blocked for a property
CREATE OR REPLACE FUNCTION is_action_blocked(
  p_property_id UUID,
  p_action_type TEXT
)
RETURNS BOOLEAN AS $$
DECLARE
  v_is_blocked BOOLEAN;
BEGIN
  -- Check if there's any active lock blocking this action
  SELECT EXISTS (
    SELECT 1
    FROM workflow_locks
    WHERE property_id = p_property_id
    AND status = 'locked'
    AND p_action_type = ANY(blocked_actions)
  ) INTO v_is_blocked;
  
  RETURN COALESCE(v_is_blocked, false);
END;
$$ LANGUAGE plpgsql;

-- Function 2: Get all active locks for a property
CREATE OR REPLACE FUNCTION get_active_locks(
  p_property_id UUID
)
RETURNS TABLE (
  lock_id UUID,
  lock_type VARCHAR(50),
  lock_reason VARCHAR(255),
  locked_at TIMESTAMP,
  blocked_actions TEXT[]
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    id,
    workflow_locks.lock_type,
    lock_reason,
    locked_at,
    workflow_locks.blocked_actions
  FROM workflow_locks
  WHERE property_id = p_property_id
  AND status = 'locked'
  ORDER BY locked_at DESC;
END;
$$ LANGUAGE plpgsql;

-- Function 3: Create lock from critical alert
CREATE OR REPLACE FUNCTION create_lock_from_alert(
  p_alert_id UUID,
  p_blocked_actions TEXT[] DEFAULT ARRAY['refinance', 'sell', 'dispose']
)
RETURNS UUID AS $$
DECLARE
  v_lock_id UUID;
  v_property_id UUID;
  v_alert_type VARCHAR(50);
  v_severity VARCHAR(20);
  v_lock_type VARCHAR(50);
BEGIN
  -- Get alert details
  SELECT property_id, alert_type, severity_level
  INTO v_property_id, v_alert_type, v_severity
  FROM committee_alerts
  WHERE id = p_alert_id;
  
  -- Determine lock type based on alert type
  v_lock_type := CASE
    WHEN v_alert_type LIKE '%dscr%' THEN 'refinance_block'
    WHEN v_alert_type LIKE '%occupancy%' THEN 'sale_hold'
    ELSE 'disposition_block'
  END;
  
  -- Create the lock
  INSERT INTO workflow_locks (
    property_id,
    alert_id,
    lock_type,
    lock_reason,
    lock_severity,
    blocked_actions,
    status
  ) VALUES (
    v_property_id,
    p_alert_id,
    v_lock_type,
    'Auto-created from critical alert: ' || v_alert_type,
    v_severity,
    p_blocked_actions,
    'locked'
  )
  RETURNING id INTO v_lock_id;
  
  RETURN v_lock_id;
END;
$$ LANGUAGE plpgsql;

-- Function 4: Unlock when alert is resolved
CREATE OR REPLACE FUNCTION unlock_from_alert_resolution(
  p_alert_id UUID,
  p_unlocked_by UUID DEFAULT NULL,
  p_unlock_reason TEXT DEFAULT 'Alert resolved by committee'
)
RETURNS INTEGER AS $$
DECLARE
  v_unlocked_count INTEGER;
BEGIN
  -- Unlock all locks associated with this alert
  UPDATE workflow_locks
  SET 
    status = 'unlocked',
    unlocked_at = CURRENT_TIMESTAMP,
    unlocked_by = p_unlocked_by,
    unlock_reason = p_unlock_reason
  WHERE alert_id = p_alert_id
  AND status = 'locked';
  
  GET DIAGNOSTICS v_unlocked_count = ROW_COUNT;
  RETURN v_unlocked_count;
END;
$$ LANGUAGE plpgsql;

-- Function 5: Auto-expire old locks
CREATE OR REPLACE FUNCTION expire_old_locks(
  p_days_threshold INTEGER DEFAULT 90
)
RETURNS INTEGER AS $$
DECLARE
  v_expired_count INTEGER;
BEGIN
  -- Auto-expire locks older than threshold
  UPDATE workflow_locks
  SET 
    status = 'expired',
    unlocked_at = CURRENT_TIMESTAMP,
    unlock_reason = 'Auto-expired after ' || p_days_threshold || ' days'
  WHERE status = 'locked'
  AND locked_at < CURRENT_TIMESTAMP - (p_days_threshold || ' days')::INTERVAL;
  
  GET DIAGNOSTICS v_expired_count = ROW_COUNT;
  RETURN v_expired_count;
END;
$$ LANGUAGE plpgsql;

-- Function 6: Get workflow lock summary for property
CREATE OR REPLACE FUNCTION get_lock_summary(
  p_property_id UUID
)
RETURNS JSON AS $$
DECLARE
  v_summary JSON;
BEGIN
  SELECT json_build_object(
    'property_id', p_property_id,
    'total_locks', COUNT(*),
    'active_locks', COUNT(*) FILTER (WHERE status = 'locked'),
    'unlocked_locks', COUNT(*) FILTER (WHERE status = 'unlocked'),
    'expired_locks', COUNT(*) FILTER (WHERE status = 'expired'),
    'critical_locks', COUNT(*) FILTER (WHERE status = 'locked' AND lock_severity = 'critical'),
    'warning_locks', COUNT(*) FILTER (WHERE status = 'locked' AND lock_severity = 'warning'),
    'all_blocked_actions', (
      SELECT array_agg(DISTINCT action)
      FROM workflow_locks, unnest(blocked_actions) AS action
      WHERE property_id = p_property_id AND status = 'locked'
    ),
    'oldest_lock_date', MIN(locked_at) FILTER (WHERE status = 'locked'),
    'avg_lock_duration_hours', AVG(lock_duration_hours) FILTER (WHERE lock_duration_hours IS NOT NULL)
  ) INTO v_summary
  FROM workflow_locks
  WHERE property_id = p_property_id;
  
  RETURN v_summary;
END;
$$ LANGUAGE plpgsql;

-- Function 7: Get all blocked actions for property (for UI)
CREATE OR REPLACE FUNCTION get_blocked_actions_for_property(
  p_property_id UUID
)
RETURNS TEXT[] AS $$
DECLARE
  v_blocked_actions TEXT[];
BEGIN
  -- Get unique list of all blocked actions from active locks
  SELECT array_agg(DISTINCT action)
  INTO v_blocked_actions
  FROM workflow_locks, unnest(blocked_actions) AS action
  WHERE property_id = p_property_id
  AND status = 'locked';
  
  RETURN COALESCE(v_blocked_actions, ARRAY[]::TEXT[]);
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- COMMENTS
-- =============================================================================

COMMENT ON TABLE workflow_locks IS 'Enforces BR-003 workflow governance - tracks blocked actions when critical alerts exist';
COMMENT ON COLUMN workflow_locks.lock_type IS 'Type of lock: acquisition_freeze, refinance_block, sale_hold, disposition_block';
COMMENT ON COLUMN workflow_locks.blocked_actions IS 'Array of actions that are blocked: refinance, sell, dispose, acquisition';
COMMENT ON COLUMN workflow_locks.lock_duration_hours IS 'Auto-calculated when unlocked (hours between locked_at and unlocked_at)';
COMMENT ON COLUMN workflow_locks.status IS 'locked (active), unlocked (manually released), expired (auto-expired)';

-- =============================================================================
-- SAMPLE USAGE
-- =============================================================================

/*
-- Example 1: Check if refinancing is blocked
SELECT is_action_blocked('property-uuid-here', 'refinance');

-- Example 2: Get all active locks for a property
SELECT * FROM get_active_locks('property-uuid-here');

-- Example 3: Create lock from critical alert
SELECT create_lock_from_alert('alert-uuid-here', ARRAY['refinance', 'sell']);

-- Example 4: Unlock when committee approves alert
SELECT unlock_from_alert_resolution('alert-uuid-here', 'user-uuid', 'Committee approved action');

-- Example 5: Get lock summary
SELECT get_lock_summary('property-uuid-here');

-- Example 6: Check what actions are blocked
SELECT get_blocked_actions_for_property('property-uuid-here');

-- Example 7: Auto-expire locks older than 90 days
SELECT expire_old_locks(90);
*/

-- =============================================================================
-- MIGRATION COMPLETE
-- =============================================================================

-- Success message
DO $$
BEGIN
  RAISE NOTICE '✅ Migration 006 completed successfully';
  RAISE NOTICE '📊 Created: workflow_locks table';
  RAISE NOTICE '📈 Indexes: 7';
  RAISE NOTICE '🔒 Constraints: 4';
  RAISE NOTICE '⚡ Triggers: 3';
  RAISE NOTICE '🔧 Functions: 7';
  RAISE NOTICE '🎯 Purpose: Enforce BR-003 workflow governance';
END $$;

















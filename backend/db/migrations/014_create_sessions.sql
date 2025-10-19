-- Migration 014: Create User Sessions Table
-- Purpose: Manage JWT tokens, refresh tokens, and session lifecycle
-- Required for: Authentication, session management, token revocation
-- Date: 2025-10-12

-- ============================================================================
-- USER_SESSIONS TABLE: Session management and token storage
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  -- Session Tokens
  session_token VARCHAR(500) NOT NULL UNIQUE, -- JWT access token (or hash)
  refresh_token VARCHAR(500), -- Refresh token for token renewal
  
  -- Device/Browser Information
  ip_address INET,
  user_agent TEXT,
  device_type VARCHAR(50), -- 'desktop', 'mobile', 'tablet', 'api'
  device_name VARCHAR(255), -- Human-readable device name
  
  -- Timing
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP NOT NULL,
  last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  -- Status
  is_active BOOLEAN DEFAULT true,
  revoked_at TIMESTAMP,
  revoked_reason VARCHAR(255)
);

-- ============================================================================
-- INDEXES: Optimized for session lookup and management
-- ============================================================================

-- User's sessions
CREATE INDEX idx_sessions_user_id ON user_sessions(user_id, is_active);

-- Session token lookup (most common)
CREATE INDEX idx_sessions_token ON user_sessions(session_token) WHERE is_active = true;

-- Refresh token lookup
CREATE INDEX idx_sessions_refresh_token ON user_sessions(refresh_token) WHERE refresh_token IS NOT NULL;

-- Expired sessions cleanup
CREATE INDEX idx_sessions_expires_at ON user_sessions(expires_at);

-- Active sessions only (partial index)
CREATE INDEX idx_sessions_active ON user_sessions(user_id, last_activity DESC) WHERE is_active = true;

-- Recently created sessions
CREATE INDEX idx_sessions_created_at ON user_sessions(created_at DESC);

-- Device type analytics
CREATE INDEX idx_sessions_device_type ON user_sessions(device_type, created_at DESC);

-- Revoked sessions (for audit)
CREATE INDEX idx_sessions_revoked ON user_sessions(revoked_at) WHERE revoked_at IS NOT NULL;

-- ============================================================================
-- CONSTRAINTS: Data validation
-- ============================================================================

-- Valid device types
ALTER TABLE user_sessions
  ADD CONSTRAINT chk_device_type 
  CHECK (device_type IS NULL OR device_type IN ('desktop', 'mobile', 'tablet', 'api', 'unknown'));

-- Session token must not be empty
ALTER TABLE user_sessions
  ADD CONSTRAINT chk_session_token_not_empty 
  CHECK (TRIM(session_token) <> '');

-- Expires_at must be after created_at
ALTER TABLE user_sessions
  ADD CONSTRAINT chk_expires_after_created 
  CHECK (expires_at > created_at);

-- Revoked_at must be after created_at
ALTER TABLE user_sessions
  ADD CONSTRAINT chk_revoked_after_created 
  CHECK (revoked_at IS NULL OR revoked_at >= created_at);

-- If revoked, should not be active
ALTER TABLE user_sessions
  ADD CONSTRAINT chk_revoked_not_active 
  CHECK ((revoked_at IS NULL) OR (is_active = false));

-- ============================================================================
-- TRIGGERS: Auto-update and cleanup
-- ============================================================================

-- Function to update last_activity on token use
CREATE OR REPLACE FUNCTION update_session_activity()
RETURNS TRIGGER AS $$
BEGIN
  NEW.last_activity = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger on session updates (but not on creation)
CREATE TRIGGER trigger_update_session_activity
  BEFORE UPDATE ON user_sessions
  FOR EACH ROW
  WHEN (OLD.last_activity IS DISTINCT FROM NEW.last_activity OR 
        OLD.is_active IS DISTINCT FROM NEW.is_active)
  EXECUTE FUNCTION update_session_activity();

-- ============================================================================
-- SESSION MANAGEMENT FUNCTIONS
-- ============================================================================

-- Function to create new session
CREATE OR REPLACE FUNCTION create_session(
  p_user_id UUID,
  p_session_token VARCHAR,
  p_refresh_token VARCHAR,
  p_ip_address INET,
  p_user_agent TEXT,
  p_device_type VARCHAR,
  p_expires_in_hours INTEGER DEFAULT 8
)
RETURNS UUID AS $$
DECLARE
  v_session_id UUID;
BEGIN
  INSERT INTO user_sessions (
    user_id, session_token, refresh_token,
    ip_address, user_agent, device_type,
    expires_at
  ) VALUES (
    p_user_id, p_session_token, p_refresh_token,
    p_ip_address, p_user_agent, p_device_type,
    CURRENT_TIMESTAMP + (p_expires_in_hours || ' hours')::INTERVAL
  )
  RETURNING id INTO v_session_id;
  
  RETURN v_session_id;
END;
$$ LANGUAGE plpgsql;

-- Function to validate session token
CREATE OR REPLACE FUNCTION validate_session(p_session_token VARCHAR)
RETURNS TABLE(
  session_id UUID,
  user_id UUID,
  is_valid BOOLEAN,
  expires_at TIMESTAMP
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    s.id as session_id,
    s.user_id,
    CASE 
      WHEN s.is_active = true 
        AND s.expires_at > CURRENT_TIMESTAMP 
        AND s.revoked_at IS NULL
      THEN true
      ELSE false
    END as is_valid,
    s.expires_at
  FROM user_sessions s
  WHERE s.session_token = p_session_token;
  
  -- If session found, update last_activity
  UPDATE user_sessions
  SET last_activity = CURRENT_TIMESTAMP
  WHERE session_token = p_session_token
    AND is_active = true;
END;
$$ LANGUAGE plpgsql;

-- Function to revoke session
CREATE OR REPLACE FUNCTION revoke_session(
  p_session_token VARCHAR,
  p_reason VARCHAR DEFAULT 'user_logout'
)
RETURNS BOOLEAN AS $$
DECLARE
  rows_affected INTEGER;
BEGIN
  UPDATE user_sessions
  SET is_active = false,
      revoked_at = CURRENT_TIMESTAMP,
      revoked_reason = p_reason
  WHERE session_token = p_session_token
    AND is_active = true;
  
  GET DIAGNOSTICS rows_affected = ROW_COUNT;
  
  RETURN rows_affected > 0;
END;
$$ LANGUAGE plpgsql;

-- Function to revoke all user sessions (logout from all devices)
CREATE OR REPLACE FUNCTION revoke_all_user_sessions(
  p_user_id UUID,
  p_reason VARCHAR DEFAULT 'logout_all_devices'
)
RETURNS INTEGER AS $$
DECLARE
  rows_affected INTEGER;
BEGIN
  UPDATE user_sessions
  SET is_active = false,
      revoked_at = CURRENT_TIMESTAMP,
      revoked_reason = p_reason
  WHERE user_id = p_user_id
    AND is_active = true;
  
  GET DIAGNOSTICS rows_affected = ROW_COUNT;
  
  RETURN rows_affected;
END;
$$ LANGUAGE plpgsql;

-- Function to cleanup expired sessions
CREATE OR REPLACE FUNCTION cleanup_expired_sessions(days_to_keep INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
  rows_deleted INTEGER;
BEGIN
  -- Delete expired and inactive sessions older than retention period
  DELETE FROM user_sessions
  WHERE expires_at < CURRENT_TIMESTAMP
    AND (is_active = false OR revoked_at IS NOT NULL)
    AND created_at < CURRENT_TIMESTAMP - (days_to_keep || ' days')::INTERVAL;
  
  GET DIAGNOSTICS rows_deleted = ROW_COUNT;
  
  RAISE NOTICE 'Deleted % expired session records (older than % days)', rows_deleted, days_to_keep;
  
  RETURN rows_deleted;
END;
$$ LANGUAGE plpgsql;

-- Function to get active sessions for a user
CREATE OR REPLACE FUNCTION get_user_active_sessions(p_user_id UUID)
RETURNS TABLE(
  session_id UUID,
  device_type VARCHAR,
  device_name VARCHAR,
  ip_address INET,
  created_at TIMESTAMP,
  last_activity TIMESTAMP,
  expires_at TIMESTAMP
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    s.id,
    s.device_type,
    s.device_name,
    s.ip_address,
    s.created_at,
    s.last_activity,
    s.expires_at
  FROM user_sessions s
  WHERE s.user_id = p_user_id
    AND s.is_active = true
    AND s.expires_at > CURRENT_TIMESTAMP
  ORDER BY s.last_activity DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to refresh session (extend expiry)
CREATE OR REPLACE FUNCTION refresh_session(
  p_refresh_token VARCHAR,
  p_new_session_token VARCHAR,
  p_new_refresh_token VARCHAR,
  p_extend_hours INTEGER DEFAULT 8
)
RETURNS UUID AS $$
DECLARE
  v_session_id UUID;
  v_user_id UUID;
BEGIN
  -- Validate refresh token and get session info
  SELECT id, user_id INTO v_session_id, v_user_id
  FROM user_sessions
  WHERE refresh_token = p_refresh_token
    AND is_active = true
    AND expires_at > CURRENT_TIMESTAMP;
  
  IF v_session_id IS NULL THEN
    RAISE EXCEPTION 'Invalid or expired refresh token';
  END IF;
  
  -- Revoke old session
  UPDATE user_sessions
  SET is_active = false,
      revoked_at = CURRENT_TIMESTAMP,
      revoked_reason = 'token_refreshed'
  WHERE id = v_session_id;
  
  -- Create new session
  INSERT INTO user_sessions (
    user_id, session_token, refresh_token,
    ip_address, user_agent, device_type,
    expires_at
  )
  SELECT 
    user_id, p_new_session_token, p_new_refresh_token,
    ip_address, user_agent, device_type,
    CURRENT_TIMESTAMP + (p_extend_hours || ' hours')::INTERVAL
  FROM user_sessions
  WHERE id = v_session_id
  RETURNING id INTO v_session_id;
  
  RETURN v_session_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TABLE COMMENTS: Documentation for database administrators
-- ============================================================================

COMMENT ON TABLE user_sessions IS 'User session management for JWT tokens and refresh tokens. Supports session validation, revocation, and cleanup. JWT tokens typically expire in 8 hours, refresh tokens in 7 days.';

COMMENT ON COLUMN user_sessions.user_id IS 'User who owns this session';
COMMENT ON COLUMN user_sessions.session_token IS 'JWT access token or hash (unique per session)';
COMMENT ON COLUMN user_sessions.refresh_token IS 'Refresh token for extending session';

COMMENT ON COLUMN user_sessions.ip_address IS 'IP address of client';
COMMENT ON COLUMN user_sessions.user_agent IS 'Browser/client user agent string';
COMMENT ON COLUMN user_sessions.device_type IS 'Device type: desktop, mobile, tablet, api';
COMMENT ON COLUMN user_sessions.device_name IS 'Human-readable device name';

COMMENT ON COLUMN user_sessions.created_at IS 'When session was created';
COMMENT ON COLUMN user_sessions.expires_at IS 'When session expires (JWT expiry)';
COMMENT ON COLUMN user_sessions.last_activity IS 'Last time session was used';

COMMENT ON COLUMN user_sessions.is_active IS 'Whether session is currently active';
COMMENT ON COLUMN user_sessions.revoked_at IS 'When session was revoked (if applicable)';
COMMENT ON COLUMN user_sessions.revoked_reason IS 'Reason for revocation: user_logout, token_refreshed, security_breach';

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Verify table creation
DO $$
BEGIN
  IF EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name = 'user_sessions'
  ) THEN
    RAISE NOTICE 'user_sessions table created successfully';
  ELSE
    RAISE EXCEPTION 'user_sessions table creation failed';
  END IF;
END $$;

-- ============================================================================
-- USAGE EXAMPLES (for developers)
-- ============================================================================

-- Example 1: Create a new session (login)
-- SELECT create_session(
--   'user-uuid-here'::UUID,
--   'jwt.access.token.here',
--   'refresh.token.here',
--   '192.168.1.100'::INET,
--   'Mozilla/5.0 (Windows NT 10.0; Win64; x64)...',
--   'desktop',
--   8  -- expires in 8 hours
-- );

-- Example 2: Validate session token
-- SELECT * FROM validate_session('jwt.access.token.here');

-- Example 3: Revoke session (logout)
-- SELECT revoke_session('jwt.access.token.here', 'user_logout');

-- Example 4: Revoke all user sessions (logout from all devices)
-- SELECT revoke_all_user_sessions('user-uuid-here', 'logout_all_devices');

-- Example 5: Get user's active sessions
-- SELECT * FROM get_user_active_sessions('user-uuid-here');

-- Example 6: Refresh session (extend expiry)
-- SELECT refresh_session(
--   'old.refresh.token',
--   'new.jwt.token',
--   'new.refresh.token',
--   8  -- extend 8 hours
-- );

-- Example 7: Cleanup expired sessions
-- SELECT cleanup_expired_sessions(30); -- Delete sessions older than 30 days

-- Example 8: List all active sessions for a user
-- SELECT 
--   device_type,
--   ip_address,
--   created_at,
--   last_activity,
--   expires_at
-- FROM user_sessions
-- WHERE user_id = 'user-uuid-here'
--   AND is_active = true
--   AND expires_at > CURRENT_TIMESTAMP
-- ORDER BY last_activity DESC;

-- Example 9: Session analytics
-- SELECT 
--   device_type,
--   COUNT(*) as session_count,
--   COUNT(*) FILTER (WHERE is_active = true) as active_sessions,
--   AVG(EXTRACT(EPOCH FROM (expires_at - created_at)) / 3600) as avg_duration_hours
-- FROM user_sessions
-- WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '7 days'
-- GROUP BY device_type
-- ORDER BY session_count DESC;

-- Example 10: Recent logins
-- SELECT 
--   u.email,
--   u.first_name,
--   u.last_name,
--   s.created_at as login_time,
--   s.ip_address,
--   s.device_type
-- FROM user_sessions s
-- JOIN users u ON u.id = s.user_id
-- WHERE s.created_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
-- ORDER BY s.created_at DESC;

-- Example 11: Concurrent sessions per user
-- SELECT 
--   u.email,
--   COUNT(*) as active_sessions,
--   STRING_AGG(s.device_type, ', ') as devices
-- FROM user_sessions s
-- JOIN users u ON u.id = s.user_id
-- WHERE s.is_active = true
--   AND s.expires_at > CURRENT_TIMESTAMP
-- GROUP BY u.id, u.email
-- HAVING COUNT(*) > 1
-- ORDER BY active_sessions DESC;

-- Example 12: Revoked sessions report
-- SELECT 
--   revoked_reason,
--   COUNT(*) as count,
--   DATE(revoked_at) as revocation_date
-- FROM user_sessions
-- WHERE revoked_at >= CURRENT_TIMESTAMP - INTERVAL '7 days'
-- GROUP BY revoked_reason, DATE(revoked_at)
-- ORDER BY revocation_date DESC, count DESC;

-- Example 13: Session expiry distribution
-- SELECT 
--   DATE_TRUNC('hour', expires_at) as expiry_hour,
--   COUNT(*) as sessions_expiring
-- FROM user_sessions
-- WHERE is_active = true
--   AND expires_at BETWEEN CURRENT_TIMESTAMP AND CURRENT_TIMESTAMP + INTERVAL '24 hours'
-- GROUP BY DATE_TRUNC('hour', expires_at)
-- ORDER BY expiry_hour;

-- Example 14: User session history
-- SELECT 
--   created_at,
--   device_type,
--   ip_address,
--   CASE 
--     WHEN is_active = true AND expires_at > CURRENT_TIMESTAMP THEN 'Active'
--     WHEN revoked_at IS NOT NULL THEN 'Revoked: ' || revoked_reason
--     WHEN expires_at <= CURRENT_TIMESTAMP THEN 'Expired'
--     ELSE 'Inactive'
--   END as status,
--   EXTRACT(EPOCH FROM (COALESCE(revoked_at, expires_at) - created_at)) / 3600 as duration_hours
-- FROM user_sessions
-- WHERE user_id = 'user-uuid-here'
-- ORDER BY created_at DESC
-- LIMIT 20;


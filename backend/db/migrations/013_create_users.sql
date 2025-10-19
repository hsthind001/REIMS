-- Migration 013: Create Users Table
-- Purpose: Authentication, authorization, and role-based access control
-- Required by: BR-008 (security & access control)
-- Date: 2025-10-12

-- ============================================================================
-- USERS TABLE: Authentication and authorization
-- ============================================================================

CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Account Information
  email VARCHAR(255) NOT NULL UNIQUE,
  username VARCHAR(100) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL, -- bcrypt hash (NEVER store plain text)
  
  -- Profile
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  phone VARCHAR(20),
  
  -- Role & Permissions
  role VARCHAR(50) NOT NULL DEFAULT 'viewer', -- 'supervisor', 'analyst', 'viewer'
  permissions VARCHAR(50)[], -- Additional granular permissions
  committee_member VARCHAR(255), -- Which committee (if any)
  
  -- Account Status
  is_active BOOLEAN DEFAULT true,
  is_email_verified BOOLEAN DEFAULT false,
  email_verified_at TIMESTAMP,
  
  -- Access Control & Security
  last_login TIMESTAMP,
  last_login_ip INET,
  failed_login_attempts INTEGER DEFAULT 0,
  account_locked_until TIMESTAMP,
  
  -- Multi-Factor Authentication
  mfa_enabled BOOLEAN DEFAULT false,
  mfa_secret VARCHAR(255), -- TOTP secret (encrypted)
  
  -- Audit
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_by UUID, -- Admin who created this user
  password_changed_at TIMESTAMP
);

-- ============================================================================
-- INDEXES: Optimized for authentication and authorization queries
-- ============================================================================

-- Email lookup (most common login method)
CREATE UNIQUE INDEX idx_users_email_lower ON users(LOWER(email));

-- Username lookup (alternate login method)
CREATE UNIQUE INDEX idx_users_username_lower ON users(LOWER(username));

-- Role-based queries
CREATE INDEX idx_users_role ON users(role);

-- Active users (most queries filter by this)
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = true;

-- Email verification status
CREATE INDEX idx_users_email_verified ON users(is_email_verified) WHERE is_email_verified = false;

-- Locked accounts (for admin review)
CREATE INDEX idx_users_locked ON users(account_locked_until) WHERE account_locked_until IS NOT NULL;

-- MFA-enabled users
CREATE INDEX idx_users_mfa ON users(mfa_enabled) WHERE mfa_enabled = true;

-- Last login tracking
CREATE INDEX idx_users_last_login ON users(last_login DESC);

-- Committee members
CREATE INDEX idx_users_committee ON users(committee_member) WHERE committee_member IS NOT NULL;

-- ============================================================================
-- CONSTRAINTS: Data validation and security rules
-- ============================================================================

-- Valid roles
ALTER TABLE users
  ADD CONSTRAINT chk_role 
  CHECK (role IN ('supervisor', 'analyst', 'viewer', 'admin'));

-- Email format (basic validation)
ALTER TABLE users
  ADD CONSTRAINT chk_email_format 
  CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

-- Username format (alphanumeric, underscore, hyphen)
ALTER TABLE users
  ADD CONSTRAINT chk_username_format 
  CHECK (username ~* '^[a-zA-Z0-9_-]{3,100}$');

-- Email must not be empty after trim
ALTER TABLE users
  ADD CONSTRAINT chk_email_not_empty 
  CHECK (TRIM(email) <> '');

-- Username must not be empty after trim
ALTER TABLE users
  ADD CONSTRAINT chk_username_not_empty 
  CHECK (TRIM(username) <> '');

-- Password hash must be bcrypt format ($2a$, $2b$, $2y$)
ALTER TABLE users
  ADD CONSTRAINT chk_password_hash_format 
  CHECK (password_hash ~* '^\$2[aby]\$\d{2}\$.{53}$');

-- Failed login attempts must be non-negative
ALTER TABLE users
  ADD CONSTRAINT chk_failed_attempts 
  CHECK (failed_login_attempts >= 0);

-- Account lock must be in the future if set
ALTER TABLE users
  ADD CONSTRAINT chk_account_locked 
  CHECK (account_locked_until IS NULL OR account_locked_until > CURRENT_TIMESTAMP);

-- Email verified timestamp only if verified
ALTER TABLE users
  ADD CONSTRAINT chk_email_verified_timestamp 
  CHECK ((is_email_verified = false AND email_verified_at IS NULL) OR 
         (is_email_verified = true AND email_verified_at IS NOT NULL));

-- MFA secret only if MFA enabled
ALTER TABLE users
  ADD CONSTRAINT chk_mfa_secret 
  CHECK ((mfa_enabled = false AND mfa_secret IS NULL) OR 
         (mfa_enabled = true AND mfa_secret IS NOT NULL));

-- Phone format (if provided)
ALTER TABLE users
  ADD CONSTRAINT chk_phone_format 
  CHECK (phone IS NULL OR phone ~* '^\+?[\d\s\-\(\)]{10,20}$');

-- ============================================================================
-- TRIGGERS: Auto-update timestamp and security
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_user_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update timestamp
CREATE TRIGGER trigger_update_user_timestamp
  BEFORE UPDATE ON users
  FOR EACH ROW
  EXECUTE FUNCTION update_user_timestamp();

-- Function to track password changes
CREATE OR REPLACE FUNCTION track_password_change()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.password_hash IS DISTINCT FROM OLD.password_hash THEN
    NEW.password_changed_at = CURRENT_TIMESTAMP;
    -- Reset failed login attempts on password change
    NEW.failed_login_attempts = 0;
    -- Clear account lock on password change
    NEW.account_locked_until = NULL;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to track password changes
CREATE TRIGGER trigger_track_password_change
  BEFORE UPDATE ON users
  FOR EACH ROW
  EXECUTE FUNCTION track_password_change();

-- ============================================================================
-- SECURITY FUNCTIONS: Authentication helpers
-- ============================================================================

-- Function to check if account is locked
CREATE OR REPLACE FUNCTION is_account_locked(user_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
  lock_until TIMESTAMP;
BEGIN
  SELECT account_locked_until INTO lock_until
  FROM users
  WHERE id = user_id;
  
  -- If no lock time set, not locked
  IF lock_until IS NULL THEN
    RETURN false;
  END IF;
  
  -- If lock time has passed, unlock and return false
  IF lock_until <= CURRENT_TIMESTAMP THEN
    UPDATE users
    SET account_locked_until = NULL,
        failed_login_attempts = 0
    WHERE id = user_id;
    RETURN false;
  END IF;
  
  -- Still locked
  RETURN true;
END;
$$ LANGUAGE plpgsql;

-- Function to record failed login attempt
CREATE OR REPLACE FUNCTION record_failed_login(user_email VARCHAR)
RETURNS void AS $$
DECLARE
  current_attempts INTEGER;
  max_attempts INTEGER := 5;
  lock_duration INTERVAL := INTERVAL '30 minutes';
BEGIN
  -- Increment failed attempts
  UPDATE users
  SET failed_login_attempts = failed_login_attempts + 1,
      updated_at = CURRENT_TIMESTAMP
  WHERE email = user_email
  RETURNING failed_login_attempts INTO current_attempts;
  
  -- Lock account if max attempts reached
  IF current_attempts >= max_attempts THEN
    UPDATE users
    SET account_locked_until = CURRENT_TIMESTAMP + lock_duration
    WHERE email = user_email;
    
    RAISE NOTICE 'Account locked for % minutes due to % failed login attempts', 
      EXTRACT(MINUTE FROM lock_duration), max_attempts;
  END IF;
END;
$$ LANGUAGE plpgsql;

-- Function to record successful login
CREATE OR REPLACE FUNCTION record_successful_login(user_id UUID, login_ip INET)
RETURNS void AS $$
BEGIN
  UPDATE users
  SET last_login = CURRENT_TIMESTAMP,
      last_login_ip = login_ip,
      failed_login_attempts = 0,
      account_locked_until = NULL
  WHERE id = user_id;
END;
$$ LANGUAGE plpgsql;

-- Function to get user permissions
CREATE OR REPLACE FUNCTION get_user_permissions(user_id UUID)
RETURNS TABLE(
  user_role VARCHAR,
  can_create BOOLEAN,
  can_read BOOLEAN,
  can_update BOOLEAN,
  can_delete BOOLEAN,
  can_approve BOOLEAN,
  can_admin BOOLEAN
) AS $$
DECLARE
  u_role VARCHAR;
BEGIN
  SELECT role INTO u_role FROM users WHERE id = user_id;
  
  RETURN QUERY
  SELECT 
    u_role as user_role,
    CASE WHEN u_role IN ('supervisor', 'analyst', 'admin') THEN true ELSE false END as can_create,
    true as can_read, -- All roles can read
    CASE WHEN u_role IN ('supervisor', 'analyst', 'admin') THEN true ELSE false END as can_update,
    CASE WHEN u_role IN ('supervisor', 'admin') THEN true ELSE false END as can_delete,
    CASE WHEN u_role IN ('supervisor', 'admin') THEN true ELSE false END as can_approve,
    CASE WHEN u_role = 'admin' THEN true ELSE false END as can_admin;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TABLE COMMENTS: Documentation for database administrators
-- ============================================================================

COMMENT ON TABLE users IS 'User accounts for authentication and authorization. Required for BR-008 security & access control. Supports role-based permissions, MFA, and account security features.';

COMMENT ON COLUMN users.email IS 'User email address (unique, used for login)';
COMMENT ON COLUMN users.username IS 'Username (unique, alternate login method)';
COMMENT ON COLUMN users.password_hash IS 'bcrypt password hash (NEVER store plain text passwords)';

COMMENT ON COLUMN users.first_name IS 'User first name';
COMMENT ON COLUMN users.last_name IS 'User last name';
COMMENT ON COLUMN users.phone IS 'Contact phone number';

COMMENT ON COLUMN users.role IS 'User role: supervisor (full access), analyst (upload/view), viewer (read-only), admin (system admin)';
COMMENT ON COLUMN users.permissions IS 'Array of additional granular permissions';
COMMENT ON COLUMN users.committee_member IS 'Committee membership (if applicable)';

COMMENT ON COLUMN users.is_active IS 'Whether account is active (soft delete)';
COMMENT ON COLUMN users.is_email_verified IS 'Whether email has been verified';
COMMENT ON COLUMN users.email_verified_at IS 'When email was verified';

COMMENT ON COLUMN users.last_login IS 'Last successful login timestamp';
COMMENT ON COLUMN users.last_login_ip IS 'IP address of last login';
COMMENT ON COLUMN users.failed_login_attempts IS 'Number of consecutive failed login attempts';
COMMENT ON COLUMN users.account_locked_until IS 'Account locked until this timestamp (null if not locked)';

COMMENT ON COLUMN users.mfa_enabled IS 'Whether multi-factor authentication is enabled';
COMMENT ON COLUMN users.mfa_secret IS 'TOTP secret for MFA (encrypted, 32-character base32)';

COMMENT ON COLUMN users.created_at IS 'When user account was created';
COMMENT ON COLUMN users.updated_at IS 'When user account was last updated';
COMMENT ON COLUMN users.created_by IS 'Admin user who created this account';
COMMENT ON COLUMN users.password_changed_at IS 'When password was last changed';

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Verify table creation
DO $$
BEGIN
  IF EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name = 'users'
  ) THEN
    RAISE NOTICE 'users table created successfully';
  ELSE
    RAISE EXCEPTION 'users table creation failed';
  END IF;
END $$;

-- ============================================================================
-- USAGE EXAMPLES (for developers)
-- ============================================================================

-- Example 1: Create a new user (supervisor)
-- Note: In production, use bcrypt to hash passwords (e.g., Python's bcrypt library)
-- INSERT INTO users (
--   email, username, password_hash,
--   first_name, last_name, role,
--   is_email_verified, email_verified_at
-- ) VALUES (
--   'john.doe@reims.com', 'johndoe',
--   '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYb7YgP5.rO', -- Example bcrypt hash
--   'John', 'Doe', 'supervisor',
--   true, CURRENT_TIMESTAMP
-- );

-- Example 2: Create an analyst user
-- INSERT INTO users (
--   email, username, password_hash,
--   first_name, last_name, role,
--   permissions
-- ) VALUES (
--   'jane.smith@reims.com', 'janesmith',
--   '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYb7YgP5.rO',
--   'Jane', 'Smith', 'analyst',
--   ARRAY['upload_documents', 'view_analytics']
-- );

-- Example 3: Create a committee member
-- INSERT INTO users (
--   email, username, password_hash,
--   first_name, last_name, role,
--   committee_member
-- ) VALUES (
--   'bob.wilson@reims.com', 'bobwilson',
--   '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYb7YgP5.rO',
--   'Bob', 'Wilson', 'supervisor',
--   'Investment Committee'
-- );

-- Example 4: Authenticate user (login)
-- SELECT id, email, password_hash, role, is_active
-- FROM users
-- WHERE LOWER(email) = LOWER('john.doe@reims.com')
--   AND is_active = true;
-- -- Then verify password hash using bcrypt.verify(plain_password, password_hash)

-- Example 5: Check if account is locked
-- SELECT is_account_locked('user-uuid-here');

-- Example 6: Record failed login attempt
-- SELECT record_failed_login('john.doe@reims.com');

-- Example 7: Record successful login
-- SELECT record_successful_login('user-uuid-here', '192.168.1.100'::INET);

-- Example 8: Get user permissions
-- SELECT * FROM get_user_permissions('user-uuid-here');

-- Example 9: Enable MFA for user
-- UPDATE users
-- SET mfa_enabled = true,
--     mfa_secret = 'JBSWY3DPEHPK3PXP' -- Base32 encoded secret
-- WHERE id = 'user-uuid-here';

-- Example 10: Verify email
-- UPDATE users
-- SET is_email_verified = true,
--     email_verified_at = CURRENT_TIMESTAMP
-- WHERE id = 'user-uuid-here';

-- Example 11: Change password
-- UPDATE users
-- SET password_hash = '$2b$12$NewHashHere...'
-- WHERE id = 'user-uuid-here';
-- -- password_changed_at will be automatically updated by trigger

-- Example 12: Deactivate user (soft delete)
-- UPDATE users
-- SET is_active = false
-- WHERE id = 'user-uuid-here';

-- Example 13: List all active supervisors
-- SELECT id, email, first_name, last_name, last_login
-- FROM users
-- WHERE role = 'supervisor'
--   AND is_active = true
-- ORDER BY last_login DESC;

-- Example 14: Find users with failed login attempts
-- SELECT email, failed_login_attempts, account_locked_until
-- FROM users
-- WHERE failed_login_attempts > 0
--   OR account_locked_until IS NOT NULL
-- ORDER BY failed_login_attempts DESC;

-- Example 15: List committee members
-- SELECT 
--   committee_member,
--   COUNT(*) as member_count,
--   STRING_AGG(first_name || ' ' || last_name, ', ') as members
-- FROM users
-- WHERE committee_member IS NOT NULL
--   AND is_active = true
-- GROUP BY committee_member;

-- Example 16: Users who haven't verified email
-- SELECT email, first_name, last_name, created_at
-- FROM users
-- WHERE is_email_verified = false
--   AND is_active = true
--   AND created_at < CURRENT_TIMESTAMP - INTERVAL '7 days'
-- ORDER BY created_at ASC;

-- Example 17: Password expiry report (90 days)
-- SELECT email, first_name, last_name, 
--        password_changed_at,
--        CURRENT_TIMESTAMP - password_changed_at as password_age
-- FROM users
-- WHERE password_changed_at < CURRENT_TIMESTAMP - INTERVAL '90 days'
--   AND is_active = true
-- ORDER BY password_changed_at ASC;

-- Example 18: User activity report
-- SELECT 
--   role,
--   COUNT(*) as total_users,
--   COUNT(*) FILTER (WHERE is_active = true) as active_users,
--   COUNT(*) FILTER (WHERE last_login >= CURRENT_TIMESTAMP - INTERVAL '30 days') as active_last_30_days,
--   COUNT(*) FILTER (WHERE mfa_enabled = true) as mfa_enabled_count
-- FROM users
-- GROUP BY role
-- ORDER BY total_users DESC;


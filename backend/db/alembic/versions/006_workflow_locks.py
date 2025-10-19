"""006_create_workflow_locks

Revision ID: 006
Revises: 005
Create Date: 2025-10-12

Purpose: Enforce BR-003 workflow governance by tracking blocked actions when critical alerts exist
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY, TEXT

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    """Create workflow_locks table and associated functions/triggers"""
    
    # Create workflow_locks table
    op.create_table(
        'workflow_locks',
        sa.Column('id', UUID, primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('property_id', UUID, sa.ForeignKey('properties.id', ondelete='CASCADE'), nullable=False),
        sa.Column('alert_id', UUID, sa.ForeignKey('committee_alerts.id', ondelete='CASCADE'), nullable=False),
        
        # Lock Information
        sa.Column('lock_type', sa.String(50), nullable=False),
        sa.Column('lock_reason', sa.String(255)),
        sa.Column('lock_severity', sa.String(20), nullable=False, server_default='critical'),
        
        # Lock Timeline
        sa.Column('locked_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('unlocked_at', sa.TIMESTAMP),
        sa.Column('lock_duration_hours', sa.Integer),
        
        # Lock Status
        sa.Column('status', sa.String(20), nullable=False, server_default='locked'),
        
        # Who locked/unlocked
        sa.Column('locked_by', UUID),
        sa.Column('unlocked_by', UUID),
        sa.Column('unlock_reason', sa.TEXT),
        
        # Blocked Actions
        sa.Column('blocked_actions', ARRAY(TEXT), server_default=sa.text("ARRAY[]::TEXT[]")),
        
        # Notifications
        sa.Column('lock_notification_sent', sa.Boolean, server_default='false'),
        sa.Column('unlock_notification_sent', sa.Boolean, server_default='false'),
        
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    
    # Create indexes
    op.create_index('idx_locks_property_id', 'workflow_locks', ['property_id'])
    op.create_index('idx_locks_alert_id', 'workflow_locks', ['alert_id'])
    op.create_index('idx_locks_status', 'workflow_locks', ['status'])
    op.create_index('idx_locks_locked_at', 'workflow_locks', [sa.text('locked_at DESC')])
    op.create_index('idx_locks_property_status', 'workflow_locks', ['property_id', 'status'])
    op.create_index('idx_locks_lock_type', 'workflow_locks', ['lock_type'])
    op.create_index('idx_locks_severity', 'workflow_locks', ['lock_severity'])
    
    # Create constraints
    op.create_check_constraint(
        'chk_lock_status',
        'workflow_locks',
        "status IN ('locked', 'unlocked', 'expired')"
    )
    
    op.create_check_constraint(
        'chk_lock_severity',
        'workflow_locks',
        "lock_severity IN ('critical', 'warning')"
    )
    
    op.create_check_constraint(
        'chk_lock_type_valid',
        'workflow_locks',
        "lock_type IN ('acquisition_freeze', 'refinance_block', 'sale_hold', 'disposition_block')"
    )
    
    op.create_check_constraint(
        'chk_unlock_after_lock',
        'workflow_locks',
        'unlocked_at IS NULL OR unlocked_at >= locked_at'
    )
    
    # Create triggers and functions using raw SQL
    op.execute("""
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
    """)
    
    op.execute("""
        -- Trigger 2: Auto-calculate lock_duration_hours when unlocked
        CREATE OR REPLACE FUNCTION calculate_lock_duration()
        RETURNS TRIGGER AS $$
        BEGIN
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
    """)
    
    op.execute("""
        -- Trigger 3: Sync property has_active_alerts flag
        CREATE OR REPLACE FUNCTION sync_property_workflow_lock()
        RETURNS TRIGGER AS $$
        BEGIN
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
    """)
    
    # Create business logic functions
    op.execute("""
        -- Function 1: Check if specific action is blocked
        CREATE OR REPLACE FUNCTION is_action_blocked(
          p_property_id UUID,
          p_action_type TEXT
        )
        RETURNS BOOLEAN AS $$
        DECLARE
          v_is_blocked BOOLEAN;
        BEGIN
          SELECT EXISTS (
            SELECT 1 FROM workflow_locks
            WHERE property_id = p_property_id
            AND status = 'locked'
            AND p_action_type = ANY(blocked_actions)
          ) INTO v_is_blocked;
          
          RETURN COALESCE(v_is_blocked, false);
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    op.execute("""
        -- Function 2: Get all active locks for a property
        CREATE OR REPLACE FUNCTION get_active_locks(p_property_id UUID)
        RETURNS TABLE (
          lock_id UUID,
          lock_type VARCHAR(50),
          lock_reason VARCHAR(255),
          locked_at TIMESTAMP,
          blocked_actions TEXT[]
        ) AS $$
        BEGIN
          RETURN QUERY
          SELECT id, workflow_locks.lock_type, workflow_locks.lock_reason, 
                 workflow_locks.locked_at, workflow_locks.blocked_actions
          FROM workflow_locks
          WHERE property_id = p_property_id AND status = 'locked'
          ORDER BY locked_at DESC;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    op.execute("""
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
          SELECT property_id, alert_type, severity_level
          INTO v_property_id, v_alert_type, v_severity
          FROM committee_alerts WHERE id = p_alert_id;
          
          v_lock_type := CASE
            WHEN v_alert_type LIKE '%dscr%' THEN 'refinance_block'
            WHEN v_alert_type LIKE '%occupancy%' THEN 'sale_hold'
            ELSE 'disposition_block'
          END;
          
          INSERT INTO workflow_locks (
            property_id, alert_id, lock_type, lock_reason, lock_severity,
            blocked_actions, status
          ) VALUES (
            v_property_id, p_alert_id, v_lock_type,
            'Auto-created from critical alert: ' || v_alert_type,
            v_severity, p_blocked_actions, 'locked'
          ) RETURNING id INTO v_lock_id;
          
          RETURN v_lock_id;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    op.execute("""
        -- Function 4: Unlock when alert is resolved
        CREATE OR REPLACE FUNCTION unlock_from_alert_resolution(
          p_alert_id UUID,
          p_unlocked_by UUID DEFAULT NULL,
          p_unlock_reason TEXT DEFAULT 'Alert resolved by committee'
        )
        RETURNS INTEGER AS $$
        DECLARE v_unlocked_count INTEGER;
        BEGIN
          UPDATE workflow_locks
          SET status = 'unlocked', unlocked_at = CURRENT_TIMESTAMP,
              unlocked_by = p_unlocked_by, unlock_reason = p_unlock_reason
          WHERE alert_id = p_alert_id AND status = 'locked';
          
          GET DIAGNOSTICS v_unlocked_count = ROW_COUNT;
          RETURN v_unlocked_count;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    op.execute("""
        -- Function 5: Auto-expire old locks
        CREATE OR REPLACE FUNCTION expire_old_locks(p_days_threshold INTEGER DEFAULT 90)
        RETURNS INTEGER AS $$
        DECLARE v_expired_count INTEGER;
        BEGIN
          UPDATE workflow_locks
          SET status = 'expired', unlocked_at = CURRENT_TIMESTAMP,
              unlock_reason = 'Auto-expired after ' || p_days_threshold || ' days'
          WHERE status = 'locked'
          AND locked_at < CURRENT_TIMESTAMP - (p_days_threshold || ' days')::INTERVAL;
          
          GET DIAGNOSTICS v_expired_count = ROW_COUNT;
          RETURN v_expired_count;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    op.execute("""
        -- Function 6: Get workflow lock summary
        CREATE OR REPLACE FUNCTION get_lock_summary(p_property_id UUID)
        RETURNS JSON AS $$
        DECLARE v_summary JSON;
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
          FROM workflow_locks WHERE property_id = p_property_id;
          
          RETURN v_summary;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    op.execute("""
        -- Function 7: Get blocked actions for property
        CREATE OR REPLACE FUNCTION get_blocked_actions_for_property(p_property_id UUID)
        RETURNS TEXT[] AS $$
        DECLARE v_blocked_actions TEXT[];
        BEGIN
          SELECT array_agg(DISTINCT action) INTO v_blocked_actions
          FROM workflow_locks, unnest(blocked_actions) AS action
          WHERE property_id = p_property_id AND status = 'locked';
          
          RETURN COALESCE(v_blocked_actions, ARRAY[]::TEXT[]);
        END;
        $$ LANGUAGE plpgsql;
    """)


def downgrade():
    """Drop workflow_locks table and associated functions/triggers"""
    
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS trg_workflow_locks_updated_at ON workflow_locks;")
    op.execute("DROP TRIGGER IF EXISTS trg_calculate_lock_duration ON workflow_locks;")
    op.execute("DROP TRIGGER IF EXISTS trg_sync_property_workflow_lock_insert ON workflow_locks;")
    op.execute("DROP TRIGGER IF EXISTS trg_sync_property_workflow_lock_update ON workflow_locks;")
    
    # Drop functions
    op.execute("DROP FUNCTION IF EXISTS update_workflow_locks_timestamp();")
    op.execute("DROP FUNCTION IF EXISTS calculate_lock_duration();")
    op.execute("DROP FUNCTION IF EXISTS sync_property_workflow_lock();")
    op.execute("DROP FUNCTION IF EXISTS is_action_blocked(UUID, TEXT);")
    op.execute("DROP FUNCTION IF EXISTS get_active_locks(UUID);")
    op.execute("DROP FUNCTION IF EXISTS create_lock_from_alert(UUID, TEXT[]);")
    op.execute("DROP FUNCTION IF EXISTS unlock_from_alert_resolution(UUID, UUID, TEXT);")
    op.execute("DROP FUNCTION IF EXISTS expire_old_locks(INTEGER);")
    op.execute("DROP FUNCTION IF EXISTS get_lock_summary(UUID);")
    op.execute("DROP FUNCTION IF EXISTS get_blocked_actions_for_property(UUID);")
    
    # Drop table (cascades will handle indexes and constraints)
    op.drop_table('workflow_locks')

















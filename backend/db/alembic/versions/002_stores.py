"""Create stores table

Revision ID: 002
Revises: 001
Create Date: 2025-10-12 00:00:00.000000

REIMS Stores Table Migration
Individual units/tenants within properties
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create stores table with all columns, indexes, constraints, and triggers.
    """
    
    # Create stores table
    op.create_table(
        'stores',
        
        # Primary Key
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        
        # Foreign Key
        sa.Column('property_id', UUID(as_uuid=True), nullable=False),
        
        # Unit Identification
        sa.Column('unit_number', sa.String(50), nullable=False),
        sa.Column('unit_name', sa.String(255), nullable=True),
        
        # Physical Characteristics
        sa.Column('sqft', sa.Numeric(10, 2), nullable=False),
        sa.Column('floor_number', sa.Integer(), nullable=True),
        
        # Lease Information
        sa.Column('tenant_name', sa.String(255), nullable=True),
        sa.Column('tenant_type', sa.String(50), nullable=True),
        
        # Lease Dates
        sa.Column('lease_start_date', sa.Date(), nullable=True),
        sa.Column('lease_end_date', sa.Date(), nullable=True),
        sa.Column('lease_status', sa.String(20), server_default='active', nullable=True),
        
        # Financial Terms
        sa.Column('monthly_rent', sa.Numeric(12, 2), nullable=True),
        sa.Column('annual_rent', sa.Numeric(15, 2), nullable=True),
        sa.Column('rent_escalation_pct', sa.Numeric(5, 2), nullable=True),
        sa.Column('security_deposit', sa.Numeric(12, 2), nullable=True),
        
        # Current Status
        sa.Column('status', sa.String(20), server_default='vacant', nullable=False),
        sa.Column('occupancy_date', sa.Date(), nullable=True),
        sa.Column('vacancy_date', sa.Date(), nullable=True),
        
        # Additional Terms
        sa.Column('parking_spaces', sa.Integer(), server_default='0', nullable=True),
        sa.Column('utilities_included', sa.Boolean(), server_default='false', nullable=True),
        sa.Column('common_area_maintenance_fee', sa.Numeric(10, 2), nullable=True),
        
        # Renewal Options
        sa.Column('renewal_option', sa.Boolean(), server_default='false', nullable=True),
        sa.Column('renewal_term_months', sa.Integer(), nullable=True),
        
        # Contact Information
        sa.Column('tenant_contact_name', sa.String(255), nullable=True),
        sa.Column('tenant_contact_phone', sa.String(20), nullable=True),
        sa.Column('tenant_contact_email', sa.String(255), nullable=True),
        
        # Audit Trail
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True),
        
        # Foreign Key Constraint
        sa.ForeignKeyConstraint(['property_id'], ['properties.id'], ondelete='CASCADE'),
        
        # Unique Constraint
        sa.UniqueConstraint('property_id', 'unit_number', name='uq_stores_property_unit'),
    )
    
    # Create Indexes
    op.create_index('idx_stores_property_id', 'stores', ['property_id'])
    op.create_index('idx_stores_status', 'stores', ['status'])
    op.create_index('idx_stores_property_status', 'stores', ['property_id', 'status'])
    op.create_index('idx_stores_lease_end_date', 'stores', ['lease_end_date'], postgresql_where=sa.text('lease_end_date IS NOT NULL'))
    op.create_index('idx_stores_tenant_name', 'stores', ['tenant_name'], postgresql_where=sa.text('tenant_name IS NOT NULL'))
    op.create_index('idx_stores_created_at', 'stores', ['created_at'], postgresql_using='btree', postgresql_ops={'created_at': 'DESC'})
    op.create_index('idx_stores_lease_status', 'stores', ['lease_status'])
    op.create_index('idx_stores_tenant_type', 'stores', ['tenant_type'], postgresql_where=sa.text('tenant_type IS NOT NULL'))
    op.create_index('idx_stores_unit_number', 'stores', ['unit_number'])
    
    # Add Constraints
    op.create_check_constraint('chk_sqft_positive', 'stores', sa.text('sqft > 0'))
    op.create_check_constraint('chk_rent_positive', 'stores', sa.text('monthly_rent IS NULL OR monthly_rent >= 0'))
    op.create_check_constraint('chk_lease_dates', 'stores', sa.text('lease_start_date IS NULL OR lease_end_date IS NULL OR lease_end_date >= lease_start_date'))
    op.create_check_constraint('chk_valid_status', 'stores', sa.text("status IN ('occupied', 'vacant', 'under_lease', 'maintenance')"))
    op.create_check_constraint('chk_valid_lease_status', 'stores', sa.text("lease_status IN ('active', 'expired', 'pending', 'terminated', 'month_to_month')"))
    op.create_check_constraint('chk_valid_tenant_type', 'stores', sa.text("tenant_type IS NULL OR tenant_type IN ('retail', 'office', 'restaurant', 'medical', 'fitness', 'salon', 'warehouse', 'mixed_use', 'other')"))
    op.create_check_constraint('chk_parking_non_negative', 'stores', sa.text('parking_spaces >= 0'))
    op.create_check_constraint('chk_annual_rent_consistency', 'stores', sa.text('monthly_rent IS NULL OR annual_rent IS NULL OR ABS(annual_rent - (monthly_rent * 12)) < 1.0'))
    op.create_check_constraint('chk_occupancy_date_valid', 'stores', sa.text('occupancy_date IS NULL OR occupancy_date <= CURRENT_DATE'))
    op.create_check_constraint('chk_vacancy_after_occupancy', 'stores', sa.text('occupancy_date IS NULL OR vacancy_date IS NULL OR vacancy_date >= occupancy_date'))
    
    # Create trigger function for updated_at
    op.execute("""
        CREATE OR REPLACE FUNCTION update_stores_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
          NEW.updated_at = CURRENT_TIMESTAMP;
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Create trigger
    op.execute("""
        CREATE TRIGGER trg_stores_updated_at
          BEFORE UPDATE ON stores
          FOR EACH ROW
          EXECUTE FUNCTION update_stores_updated_at();
    """)
    
    # Create function to calculate property occupancy
    op.execute("""
        CREATE OR REPLACE FUNCTION calculate_property_occupancy(p_property_id UUID)
        RETURNS DECIMAL(5, 2) AS $$
        DECLARE
          occupied_count INTEGER;
          total_count INTEGER;
          occupancy_rate DECIMAL(5, 2);
        BEGIN
          SELECT COUNT(*) INTO occupied_count
          FROM stores
          WHERE property_id = p_property_id AND status = 'occupied';
          
          SELECT COUNT(*) INTO total_count
          FROM stores
          WHERE property_id = p_property_id;
          
          IF total_count = 0 THEN
            RETURN 0;
          ELSE
            occupancy_rate := (occupied_count::DECIMAL / total_count::DECIMAL) * 100;
            RETURN ROUND(occupancy_rate, 2);
          END IF;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Create function to sync property occupancy
    op.execute("""
        CREATE OR REPLACE FUNCTION sync_property_occupancy()
        RETURNS TRIGGER AS $$
        DECLARE
          new_occupancy_rate DECIMAL(5, 2);
          occupied_count INTEGER;
          total_count INTEGER;
        BEGIN
          DECLARE
            p_id UUID;
          BEGIN
            p_id := COALESCE(NEW.property_id, OLD.property_id);
            
            SELECT 
              COUNT(*) FILTER (WHERE status = 'occupied'),
              COUNT(*)
            INTO occupied_count, total_count
            FROM stores
            WHERE property_id = p_id;
            
            IF total_count > 0 THEN
              new_occupancy_rate := (occupied_count::DECIMAL / total_count::DECIMAL) * 100;
            ELSE
              new_occupancy_rate := 0;
            END IF;
            
            UPDATE properties
            SET 
              occupied_units = occupied_count,
              total_units = total_count,
              occupancy_rate = ROUND(new_occupancy_rate, 2)
            WHERE id = p_id;
          END;
          
          RETURN COALESCE(NEW, OLD);
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Create trigger to auto-sync property occupancy
    op.execute("""
        CREATE TRIGGER trg_sync_property_occupancy
          AFTER INSERT OR UPDATE OR DELETE ON stores
          FOR EACH ROW
          EXECUTE FUNCTION sync_property_occupancy();
    """)


def downgrade() -> None:
    """
    Drop stores table and related objects.
    """
    # Drop triggers
    op.execute('DROP TRIGGER IF EXISTS trg_sync_property_occupancy ON stores')
    op.execute('DROP TRIGGER IF EXISTS trg_stores_updated_at ON stores')
    
    # Drop functions
    op.execute('DROP FUNCTION IF EXISTS sync_property_occupancy()')
    op.execute('DROP FUNCTION IF EXISTS calculate_property_occupancy(UUID)')
    op.execute('DROP FUNCTION IF EXISTS update_stores_updated_at()')
    
    # Drop table (indexes and constraints are dropped automatically)
    op.drop_table('stores')

















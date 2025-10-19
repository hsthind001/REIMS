"""Create properties table

Revision ID: 001
Revises: 
Create Date: 2025-10-12 00:00:00.000000

REIMS Properties Table Migration
Comprehensive real estate property management schema
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create properties table with all columns, indexes, constraints, and triggers.
    """
    
    # Create properties table
    op.create_table(
        'properties',
        
        # Primary Key
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        
        # Basic Information
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        
        # Location Information
        sa.Column('address', sa.Text(), nullable=False),
        sa.Column('city', sa.String(100), nullable=False),
        sa.Column('state', sa.String(50), nullable=False),
        sa.Column('zip_code', sa.String(20), nullable=True),
        sa.Column('latitude', sa.Numeric(10, 8), nullable=True),
        sa.Column('longitude', sa.Numeric(11, 8), nullable=True),
        
        # Physical Characteristics
        sa.Column('total_sqft', sa.Numeric(12, 2), nullable=True),
        sa.Column('year_built', sa.Integer(), nullable=True),
        sa.Column('property_type', sa.String(50), nullable=True),
        sa.Column('property_class', sa.String(20), nullable=True),
        
        # Financial - Acquisition
        sa.Column('acquisition_cost', sa.Numeric(15, 2), nullable=True),
        sa.Column('acquisition_date', sa.Date(), nullable=True),
        
        # Financial - Current
        sa.Column('current_value', sa.Numeric(15, 2), nullable=True),
        sa.Column('last_appraised_date', sa.Date(), nullable=True),
        sa.Column('estimated_market_value', sa.Numeric(15, 2), nullable=True),
        
        # Debt Information
        sa.Column('loan_balance', sa.Numeric(15, 2), nullable=True),
        sa.Column('original_loan_amount', sa.Numeric(15, 2), nullable=True),
        sa.Column('interest_rate', sa.Numeric(5, 3), nullable=True),
        sa.Column('loan_maturity_date', sa.Date(), nullable=True),
        sa.Column('dscr', sa.Numeric(4, 2), nullable=True),
        
        # Income Information
        sa.Column('annual_noi', sa.Numeric(15, 2), nullable=True),
        sa.Column('annual_revenue', sa.Numeric(15, 2), nullable=True),
        
        # Occupancy Information
        sa.Column('total_units', sa.Integer(), nullable=True),
        sa.Column('occupied_units', sa.Integer(), nullable=True),
        sa.Column('occupancy_rate', sa.Numeric(5, 2), nullable=True),
        
        # Status and Flags
        sa.Column('status', sa.String(20), server_default='active', nullable=False),
        sa.Column('has_active_alerts', sa.Boolean(), server_default='false', nullable=False),
        
        # Audit Trail
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True),
    )
    
    # Create Indexes
    op.create_index('idx_properties_status', 'properties', ['status'])
    op.create_index('idx_properties_city_state', 'properties', ['city', 'state'])
    op.create_index('idx_properties_property_type', 'properties', ['property_type'])
    op.create_index('idx_properties_occupancy_rate', 'properties', ['occupancy_rate'], postgresql_using='btree', postgresql_ops={'occupancy_rate': 'DESC'})
    op.create_index('idx_properties_created_at', 'properties', ['created_at'], postgresql_using='btree', postgresql_ops={'created_at': 'DESC'})
    op.create_index('idx_properties_has_alerts', 'properties', ['has_active_alerts'], postgresql_where=sa.text('has_active_alerts = true'))
    op.create_index('idx_properties_current_value', 'properties', ['current_value'], postgresql_using='btree', postgresql_ops={'current_value': 'DESC'})
    op.create_index('idx_properties_coordinates', 'properties', ['latitude', 'longitude'], postgresql_where=sa.text('latitude IS NOT NULL AND longitude IS NOT NULL'))
    op.create_index('idx_properties_class', 'properties', ['property_class'])
    
    # Add Constraints
    op.create_check_constraint(
        'chk_occupancy_rate',
        'properties',
        sa.text('occupancy_rate IS NULL OR (occupancy_rate >= 0 AND occupancy_rate <= 100)')
    )
    
    op.create_check_constraint(
        'chk_sqft_positive',
        'properties',
        sa.text('total_sqft IS NULL OR total_sqft > 0')
    )
    
    op.create_check_constraint(
        'chk_acquisition_before_current',
        'properties',
        sa.text('acquisition_date IS NULL OR acquisition_date <= CURRENT_DATE')
    )
    
    op.create_check_constraint(
        'chk_year_built_reasonable',
        'properties',
        sa.text('year_built IS NULL OR (year_built >= 1800 AND year_built <= EXTRACT(YEAR FROM CURRENT_DATE) + 5)')
    )
    
    op.create_check_constraint(
        'chk_occupied_within_total',
        'properties',
        sa.text('occupied_units IS NULL OR total_units IS NULL OR occupied_units <= total_units')
    )
    
    op.create_check_constraint(
        'chk_valid_status',
        'properties',
        sa.text("status IN ('active', 'sold', 'under_renovation', 'pending_sale', 'inactive')")
    )
    
    op.create_check_constraint(
        'chk_valid_property_type',
        'properties',
        sa.text("property_type IS NULL OR property_type IN ('office', 'retail', 'mixed-use', 'industrial', 'residential', 'warehouse')")
    )
    
    op.create_check_constraint(
        'chk_valid_property_class',
        'properties',
        sa.text("property_class IS NULL OR property_class IN ('A', 'B', 'C', 'D')")
    )
    
    # Create trigger function for updated_at
    op.execute("""
        CREATE OR REPLACE FUNCTION update_properties_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
          NEW.updated_at = CURRENT_TIMESTAMP;
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Create trigger
    op.execute("""
        CREATE TRIGGER trg_properties_updated_at
          BEFORE UPDATE ON properties
          FOR EACH ROW
          EXECUTE FUNCTION update_properties_updated_at();
    """)


def downgrade() -> None:
    """
    Drop properties table and related objects.
    """
    # Drop trigger
    op.execute('DROP TRIGGER IF EXISTS trg_properties_updated_at ON properties')
    
    # Drop trigger function
    op.execute('DROP FUNCTION IF EXISTS update_properties_updated_at()')
    
    # Drop table (indexes and constraints are dropped automatically)
    op.drop_table('properties')

















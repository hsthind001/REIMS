"""Create financial_documents table

Revision ID: 003
Revises: 002
Create Date: 2025-10-12 00:00:00.000000

REIMS Financial Documents Table Migration
Document tracking and processing status
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create financial_documents table with all columns, indexes, constraints, triggers, and functions.
    """
    
    # Create financial_documents table
    op.create_table(
        'financial_documents',
        
        # Primary Key
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        
        # Foreign Key
        sa.Column('property_id', UUID(as_uuid=True), nullable=False),
        
        # File Information
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_path', sa.Text(), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=True),
        sa.Column('file_hash', sa.String(64), nullable=True),
        sa.Column('mime_type', sa.String(50), nullable=True),
        
        # Document Classification
        sa.Column('document_type', sa.String(50), nullable=False),
        sa.Column('document_name', sa.String(255), nullable=True),
        
        # Processing Status
        sa.Column('status', sa.String(20), server_default='queued', nullable=False),
        sa.Column('processing_status_detail', sa.String(255), nullable=True),
        
        # Dates
        sa.Column('upload_date', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('document_date', sa.Date(), nullable=True),
        sa.Column('processing_start_date', sa.TIMESTAMP(), nullable=True),
        sa.Column('processing_end_date', sa.TIMESTAMP(), nullable=True),
        sa.Column('processing_duration_seconds', sa.Numeric(10, 2), nullable=True),
        
        # Extracted Data Metadata
        sa.Column('extracted_metrics_count', sa.Integer(), server_default='0', nullable=True),
        sa.Column('total_tables_found', sa.Integer(), nullable=True),
        sa.Column('total_text_pages', sa.Integer(), nullable=True),
        sa.Column('ocr_required', sa.Boolean(), server_default='false', nullable=True),
        
        # Quality/Confidence
        sa.Column('avg_extraction_confidence', sa.Numeric(3, 2), nullable=True),
        
        # Error Handling
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_code', sa.String(50), nullable=True),
        sa.Column('processing_attempts', sa.Integer(), server_default='0', nullable=True),
        sa.Column('last_error_at', sa.TIMESTAMP(), nullable=True),
        
        # AI Processing
        sa.Column('ai_summary_generated', sa.Boolean(), server_default='false', nullable=True),
        sa.Column('ai_summary_confidence', sa.Numeric(3, 2), nullable=True),
        
        # Audit & Security
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('reviewed_by', UUID(as_uuid=True), nullable=True),
        sa.Column('reviewed_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        
        # Foreign Key Constraint
        sa.ForeignKeyConstraint(['property_id'], ['properties.id'], ondelete='CASCADE'),
    )
    
    # Create Indexes
    op.create_index('idx_docs_property_id', 'financial_documents', ['property_id'])
    op.create_index('idx_docs_status', 'financial_documents', ['status'])
    op.create_index('idx_docs_property_status', 'financial_documents', ['property_id', 'status'])
    op.create_index('idx_docs_upload_date', 'financial_documents', ['upload_date'], postgresql_using='btree', postgresql_ops={'upload_date': 'DESC'})
    op.create_index('idx_docs_document_type', 'financial_documents', ['document_type'])
    op.create_index('idx_docs_file_hash', 'financial_documents', ['file_hash'], postgresql_where=sa.text('file_hash IS NOT NULL'))
    op.create_index('idx_docs_document_date', 'financial_documents', ['document_date'], postgresql_where=sa.text('document_date IS NOT NULL'))
    op.create_index('idx_docs_created_at', 'financial_documents', ['created_at'], postgresql_using='btree', postgresql_ops={'created_at': 'DESC'})
    op.create_index('idx_docs_processing_attempts', 'financial_documents', ['processing_attempts'], postgresql_where=sa.text("status = 'failed'"))
    
    # Add Constraints
    op.create_check_constraint('chk_status_valid', 'financial_documents', sa.text("status IN ('queued', 'processing', 'processed', 'failed', 'reviewed')"))
    op.create_check_constraint('chk_confidence', 'financial_documents', sa.text('avg_extraction_confidence IS NULL OR (avg_extraction_confidence >= 0 AND avg_extraction_confidence <= 1)'))
    op.create_check_constraint('chk_ai_confidence', 'financial_documents', sa.text('ai_summary_confidence IS NULL OR (ai_summary_confidence >= 0 AND ai_summary_confidence <= 1)'))
    op.create_check_constraint('chk_file_size_positive', 'financial_documents', sa.text('file_size_bytes IS NULL OR file_size_bytes > 0'))
    op.create_check_constraint('chk_valid_document_type', 'financial_documents', sa.text("document_type IN ('lease', 'offering_memo', 'financial_stmt', 'appraisal', 'insurance', 'tax_return', 'loan_document', 'inspection_report', 'tenant_estoppel', 'rent_roll', 'operating_statement', 'other')"))
    op.create_check_constraint('chk_processing_dates', 'financial_documents', sa.text('processing_start_date IS NULL OR processing_end_date IS NULL OR processing_end_date >= processing_start_date'))
    op.create_check_constraint('chk_processing_attempts_positive', 'financial_documents', sa.text('processing_attempts >= 0'))
    op.create_check_constraint('chk_metrics_count_positive', 'financial_documents', sa.text('extracted_metrics_count >= 0'))
    op.create_check_constraint('chk_document_date_reasonable', 'financial_documents', sa.text("document_date IS NULL OR document_date <= CURRENT_DATE + INTERVAL '1 year'"))
    
    # Create trigger function for updated_at
    op.execute("""
        CREATE OR REPLACE FUNCTION update_financial_documents_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
          NEW.updated_at = CURRENT_TIMESTAMP;
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Create trigger
    op.execute("""
        CREATE TRIGGER trg_financial_documents_updated_at
          BEFORE UPDATE ON financial_documents
          FOR EACH ROW
          EXECUTE FUNCTION update_financial_documents_updated_at();
    """)
    
    # Create trigger function for processing duration
    op.execute("""
        CREATE OR REPLACE FUNCTION calculate_processing_duration()
        RETURNS TRIGGER AS $$
        BEGIN
          IF NEW.processing_end_date IS NOT NULL AND NEW.processing_start_date IS NOT NULL THEN
            NEW.processing_duration_seconds := EXTRACT(EPOCH FROM (NEW.processing_end_date - NEW.processing_start_date));
          END IF;
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Create trigger
    op.execute("""
        CREATE TRIGGER trg_calculate_processing_duration
          BEFORE INSERT OR UPDATE ON financial_documents
          FOR EACH ROW
          EXECUTE FUNCTION calculate_processing_duration();
    """)
    
    # Create function to find duplicate documents
    op.execute("""
        CREATE OR REPLACE FUNCTION find_duplicate_documents(p_file_hash VARCHAR(64))
        RETURNS TABLE (
          doc_id UUID,
          property_id UUID,
          file_name VARCHAR(255),
          upload_date TIMESTAMP
        ) AS $$
        BEGIN
          RETURN QUERY
          SELECT 
            id,
            financial_documents.property_id,
            financial_documents.file_name,
            financial_documents.upload_date
          FROM financial_documents
          WHERE file_hash = p_file_hash
          ORDER BY upload_date DESC;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Create function to get processing stats
    op.execute("""
        CREATE OR REPLACE FUNCTION get_document_processing_stats(p_property_id UUID DEFAULT NULL)
        RETURNS TABLE (
          status VARCHAR(20),
          document_count INTEGER,
          avg_duration_seconds DECIMAL(10, 2),
          total_size_mb DECIMAL(10, 2)
        ) AS $$
        BEGIN
          RETURN QUERY
          SELECT 
            financial_documents.status,
            COUNT(*)::INTEGER as document_count,
            ROUND(AVG(processing_duration_seconds), 2) as avg_duration_seconds,
            ROUND(SUM(file_size_bytes) / 1024.0 / 1024.0, 2) as total_size_mb
          FROM financial_documents
          WHERE p_property_id IS NULL OR property_id = p_property_id
          GROUP BY financial_documents.status
          ORDER BY document_count DESC;
        END;
        $$ LANGUAGE plpgsql;
    """)


def downgrade() -> None:
    """
    Drop financial_documents table and related objects.
    """
    # Drop triggers
    op.execute('DROP TRIGGER IF EXISTS trg_calculate_processing_duration ON financial_documents')
    op.execute('DROP TRIGGER IF EXISTS trg_financial_documents_updated_at ON financial_documents')
    
    # Drop functions
    op.execute('DROP FUNCTION IF EXISTS get_document_processing_stats(UUID)')
    op.execute('DROP FUNCTION IF EXISTS find_duplicate_documents(VARCHAR)')
    op.execute('DROP FUNCTION IF EXISTS calculate_processing_duration()')
    op.execute('DROP FUNCTION IF EXISTS update_financial_documents_updated_at()')
    
    # Drop table (indexes and constraints are dropped automatically)
    op.drop_table('financial_documents')

















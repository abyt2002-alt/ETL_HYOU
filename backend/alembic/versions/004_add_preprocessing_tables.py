"""add preprocessing tables

Revision ID: 004
Revises: 003
Create Date: 2026-04-23

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # Mapping files table
    op.create_table(
        'mapping_files',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('mapping_name', sa.String(100), nullable=False),
        sa.Column('source_name', sa.String(100), nullable=False),
        sa.Column('mapping_type', sa.String(100), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('storage_path', sa.String(500), nullable=False),
        sa.Column('file_type', sa.String(50), nullable=False),
        sa.Column('required_columns', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Integer(), default=0),
        sa.Column('uploaded_at', sa.DateTime(), nullable=True),
        sa.Column('uploaded_by', sa.String(100), default='system'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_mapping_files_id', 'mapping_files', ['id'])

    # Preprocessing runs table
    op.create_table(
        'preprocessing_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('triggered_by', sa.String(100), default='system'),
        sa.Column('summary_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_preprocessing_runs_id', 'preprocessing_runs', ['id'])

    # Preprocessing run items table
    op.create_table(
        'preprocessing_run_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('run_id', sa.Integer(), nullable=False),
        sa.Column('source_name', sa.String(100), nullable=False),
        sa.Column('input_table', sa.String(100), nullable=False),
        sa.Column('output_table', sa.String(100), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('rows_read', sa.Integer(), default=0),
        sa.Column('rows_output', sa.Integer(), default=0),
        sa.Column('exact_duplicates_found', sa.Integer(), default=0),
        sa.Column('business_duplicates_found', sa.Integer(), default=0),
        sa.Column('mapping_matches', sa.Integer(), default=0),
        sa.Column('mapping_unmatched', sa.Integer(), default=0),
        sa.Column('unlabeled_count', sa.Integer(), default=0),
        sa.Column('issues_found', sa.Integer(), default=0),
        sa.Column('mapping_file_id', sa.Integer(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['run_id'], ['preprocessing_runs.id']),
        sa.ForeignKeyConstraint(['mapping_file_id'], ['mapping_files.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_preprocessing_run_items_id', 'preprocessing_run_items', ['id'])

    # Data quality issues table
    op.create_table(
        'data_quality_issues',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('run_item_id', sa.Integer(), nullable=False),
        sa.Column('source_name', sa.String(100), nullable=False),
        sa.Column('issue_type', sa.String(100), nullable=False),
        sa.Column('severity', sa.String(50), nullable=False),
        sa.Column('row_identifier', sa.String(255), nullable=True),
        sa.Column('issue_details', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['run_item_id'], ['preprocessing_run_items.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_data_quality_issues_id', 'data_quality_issues', ['id'])

    # Curated Shopify table
    op.create_table(
        'curated_shopify',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('day', sa.Date(), nullable=False),
        sa.Column('shipping_postal_code', sa.String(50), nullable=True),
        sa.Column('shipping_postal_code_cleaned', sa.String(50), nullable=True),
        sa.Column('order', sa.String(100), nullable=True),
        sa.Column('customer_type', sa.String(100), nullable=True),
        sa.Column('net_sales', sa.Numeric(10, 2), nullable=True),
        sa.Column('order_item_current_quantity', sa.Integer(), nullable=True),
        sa.Column('orders', sa.Integer(), nullable=True),
        sa.Column('dma', sa.String(255), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_curated_shopify_id', 'curated_shopify', ['id'])

    # Curated GA table
    op.create_table(
        'curated_ga',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('day', sa.Date(), nullable=False),
        sa.Column('region', sa.String(255), nullable=True),
        sa.Column('session_source', sa.String(500), nullable=True),
        sa.Column('city', sa.String(255), nullable=True),
        sa.Column('sessions', sa.Integer(), nullable=True),
        sa.Column('dma', sa.String(255), nullable=True),
        sa.Column('source_label', sa.String(100), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_curated_ga_id', 'curated_ga', ['id'])

    # Curated GAds table
    op.create_table(
        'curated_gads',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('campaign', sa.String(500), nullable=True),
        sa.Column('day', sa.Date(), nullable=False),
        sa.Column('cost', sa.Numeric(10, 2), nullable=True),
        sa.Column('impr', sa.Integer(), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_curated_gads_id', 'curated_gads', ['id'])

    # Curated Meta table
    op.create_table(
        'curated_meta',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('day', sa.Date(), nullable=False),
        sa.Column('dma_region', sa.String(255), nullable=True),
        sa.Column('impressions', sa.Integer(), nullable=True),
        sa.Column('amount_spent', sa.Numeric(10, 2), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_curated_meta_id', 'curated_meta', ['id'])


def downgrade():
    op.drop_index('ix_curated_meta_id', 'curated_meta')
    op.drop_table('curated_meta')
    
    op.drop_index('ix_curated_gads_id', 'curated_gads')
    op.drop_table('curated_gads')
    
    op.drop_index('ix_curated_ga_id', 'curated_ga')
    op.drop_table('curated_ga')
    
    op.drop_index('ix_curated_shopify_id', 'curated_shopify')
    op.drop_table('curated_shopify')
    
    op.drop_index('ix_data_quality_issues_id', 'data_quality_issues')
    op.drop_table('data_quality_issues')
    
    op.drop_index('ix_preprocessing_run_items_id', 'preprocessing_run_items')
    op.drop_table('preprocessing_run_items')
    
    op.drop_index('ix_preprocessing_runs_id', 'preprocessing_runs')
    op.drop_table('preprocessing_runs')
    
    op.drop_index('ix_mapping_files_id', 'mapping_files')
    op.drop_table('mapping_files')

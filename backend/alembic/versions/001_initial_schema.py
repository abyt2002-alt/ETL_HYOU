"""initial schema

Revision ID: 001
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('ingestion_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('trigger_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('triggered_by', sa.String(length=100), nullable=True),
        sa.Column('summary_message', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ingestion_runs_id'), 'ingestion_runs', ['id'], unique=False)

    op.create_table('ingestion_run_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('run_id', sa.Integer(), nullable=False),
        sa.Column('source_name', sa.String(length=100), nullable=False),
        sa.Column('sheet_tab_name', sa.String(length=100), nullable=False),
        sa.Column('target_table_name', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('rows_read', sa.Integer(), nullable=True),
        sa.Column('rows_loaded', sa.Integer(), nullable=True),
        sa.Column('rows_failed', sa.Integer(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['run_id'], ['ingestion_runs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ingestion_run_items_id'), 'ingestion_run_items', ['id'], unique=False)

    op.create_table('raw_meta',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('day', sa.Date(), nullable=False),
        sa.Column('dma_region', sa.String(length=255), nullable=True),
        sa.Column('impressions', sa.Integer(), nullable=True),
        sa.Column('amount_spent', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('ingested_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_raw_meta_id'), 'raw_meta', ['id'], unique=False)

    op.create_table('raw_shopify',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('day', sa.Date(), nullable=False),
        sa.Column('shipping_postal_code', sa.String(length=50), nullable=True),
        sa.Column('order', sa.String(length=100), nullable=True),
        sa.Column('customer_type', sa.String(length=100), nullable=True),
        sa.Column('net_sales', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('order_item_current_quantity', sa.Integer(), nullable=True),
        sa.Column('orders', sa.Integer(), nullable=True),
        sa.Column('ingested_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_raw_shopify_id'), 'raw_shopify', ['id'], unique=False)

    op.create_table('raw_ga',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('day', sa.Date(), nullable=False),
        sa.Column('region', sa.String(length=255), nullable=True),
        sa.Column('session_source', sa.String(length=255), nullable=True),
        sa.Column('city', sa.String(length=255), nullable=True),
        sa.Column('sessions', sa.Integer(), nullable=True),
        sa.Column('ingested_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_raw_ga_id'), 'raw_ga', ['id'], unique=False)

    op.create_table('raw_gads',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('campaign', sa.String(length=255), nullable=True),
        sa.Column('day', sa.Date(), nullable=False),
        sa.Column('cost', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('impr', sa.Integer(), nullable=True),
        sa.Column('ingested_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_raw_gads_id'), 'raw_gads', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_raw_gads_id'), table_name='raw_gads')
    op.drop_table('raw_gads')
    op.drop_index(op.f('ix_raw_ga_id'), table_name='raw_ga')
    op.drop_table('raw_ga')
    op.drop_index(op.f('ix_raw_shopify_id'), table_name='raw_shopify')
    op.drop_table('raw_shopify')
    op.drop_index(op.f('ix_raw_meta_id'), table_name='raw_meta')
    op.drop_table('raw_meta')
    op.drop_index(op.f('ix_ingestion_run_items_id'), table_name='ingestion_run_items')
    op.drop_table('ingestion_run_items')
    op.drop_index(op.f('ix_ingestion_runs_id'), table_name='ingestion_runs')
    op.drop_table('ingestion_runs')

"""update gads column

Revision ID: 002
Revises: 001
Create Date: 2026-04-23 16:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Rename column from impr to impr_
    op.alter_column('raw_gads', 'impr', new_column_name='impr_')


def downgrade():
    # Rename column back from impr_ to impr
    op.alter_column('raw_gads', 'impr_', new_column_name='impr')

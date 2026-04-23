"""increase ga varchar lengths

Revision ID: 003
Revises: 002
Create Date: 2026-04-23

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Increase VARCHAR lengths for GA table to handle longer values
    op.alter_column('raw_ga', 'session_source',
                    existing_type=sa.String(255),
                    type_=sa.String(500),
                    existing_nullable=True)
    
    # Also increase campaign length for GAds to be safe
    op.alter_column('raw_gads', 'campaign',
                    existing_type=sa.String(255),
                    type_=sa.String(500),
                    existing_nullable=True)


def downgrade():
    op.alter_column('raw_ga', 'session_source',
                    existing_type=sa.String(500),
                    type_=sa.String(255),
                    existing_nullable=True)
    
    op.alter_column('raw_gads', 'campaign',
                    existing_type=sa.String(500),
                    type_=sa.String(255),
                    existing_nullable=True)

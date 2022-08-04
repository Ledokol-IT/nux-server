"""Confirmations

Revision ID: 0b43488d8aa4
Revises: f116fd5e93cc
Create Date: 2022-07-31 18:55:52.098113

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0b43488d8aa4'
down_revision = 'f116fd5e93cc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DELETE FROM confirmations")
    op.add_column('confirmations', sa.Column(
        'dt_sent', sa.DateTime(), nullable=False))
    op.add_column('confirmations', sa.Column(
        'retries', sa.Integer(), nullable=False))
    op.create_index(op.f('ix_confirmations_phone'),
                    'confirmations', ['phone'], unique=False)
    op.drop_column('confirmations', 'dt_created')


def downgrade() -> None:
    op.execute("DELETE FROM confirmations")
    op.add_column('confirmations', sa.Column(
        'dt_created',
        postgresql.TIMESTAMP(),
        autoincrement=False,
        nullable=False,
    ))
    op.drop_index(op.f('ix_confirmations_phone'), table_name='confirmations')
    op.drop_column('confirmations', 'retries')
    op.drop_column('confirmations', 'dt_sent')

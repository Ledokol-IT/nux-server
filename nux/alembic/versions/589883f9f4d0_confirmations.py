"""confirmations

Revision ID: 589883f9f4d0
Revises: 3c67d400d75b
Create Date: 2022-07-24 16:42:27.729050

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '589883f9f4d0'
down_revision = '3c67d400d75b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'confirmations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('reason', sa.String(), nullable=False),
        sa.Column('dt_created', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.alter_column('users', 'hashed_password',
                    existing_type=sa.VARCHAR(),
                    nullable=True)


def downgrade() -> None:
    op.alter_column(
        'users',
        'hashed_password',
        existing_type=sa.VARCHAR(),
        nullable=False
    )
    op.drop_table('confirmations')

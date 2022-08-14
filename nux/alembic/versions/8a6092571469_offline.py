"""offline

Revision ID: 8a6092571469
Revises: 2960950b8fb4
Create Date: 2022-08-14 13:26:09.447399

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8a6092571469'
down_revision = '2960950b8fb4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'offline_users',
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('dt_next_ping', sa.DateTime(), nullable=False),
        sa.Column('pinged_cnt', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('user_id')
    )


def downgrade() -> None:
    op.drop_table('offline_users')

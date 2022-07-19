"""remove apps.android_category

Revision ID: 5c486b435974
Revises: 61a5e09f0174
Create Date: 2022-07-19 05:18:39.682134

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5c486b435974'
down_revision = '61a5e09f0174'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column('apps', 'android_category')


def downgrade() -> None:
    op.add_column('apps', sa.Column('android_category',
                  sa.VARCHAR(), autoincrement=False, nullable=True))

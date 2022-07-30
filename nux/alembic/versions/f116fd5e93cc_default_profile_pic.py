"""default_profile_pic

Revision ID: f116fd5e93cc
Revises: 61c1fad8f21a
Create Date: 2022-07-30 22:15:25.049330

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f116fd5e93cc'
down_revision = '61c1fad8f21a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column(
        '_default_profile_pic_id',
        sa.String(),
        nullable=True)
    )


def downgrade() -> None:
    op.drop_column('users', '_default_profile_pic_id')

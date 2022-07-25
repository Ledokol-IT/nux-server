"""rename disturb

Revision ID: fccc925ee9a4
Revises: 589883f9f4d0
Create Date: 2022-07-25 13:34:47.898930

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fccc925ee9a4'
down_revision = '589883f9f4d0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        'users',
        'do_not_disturbe_mode',
        nullable=False,
        new_column_name='do_not_disturb',
    )


def downgrade() -> None:
    op.alter_column(
        'users',
        'do_not_disturb',
        nullable=False,
        new_column_name='do_not_disturbe_mode',
    )

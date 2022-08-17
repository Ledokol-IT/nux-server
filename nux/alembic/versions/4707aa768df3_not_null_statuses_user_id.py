"""not null statuses.user_id

Revision ID: 4707aa768df3
Revises: 8a6092571469
Create Date: 2022-08-17 22:09:57.945737

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4707aa768df3'
down_revision = '8a6092571469'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DELETE FROM user_statuses_v2 WHERE user_id = NULL")
    op.alter_column(
        'user_statuses_v2', 'user_id',
        existing_type=sa.VARCHAR(),
        nullable=False
    )


def downgrade() -> None:
    op.alter_column(
        'user_statuses_v2', 'user_id',
        existing_type=sa.VARCHAR(),
        nullable=True
    )

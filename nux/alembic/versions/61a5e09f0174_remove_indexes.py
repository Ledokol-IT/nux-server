"""remove indexes

Revision ID: 61a5e09f0174
Revises: 68bb1892f945
Create Date: 2022-07-19 13:13:09.248558

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '61a5e09f0174'
down_revision = '68bb1892f945'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index('ix_apps_id', table_name='apps')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_index('ix_users_nickname', table_name='users')
    op.create_index(op.f('ix_users_nickname'),
                    'users', ['nickname'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_users_nickname'), table_name='users')
    op.create_index('ix_users_nickname', 'users', ['nickname'], unique=False)
    op.create_index('ix_users_id', 'users', ['id'], unique=False)
    op.create_index('ix_apps_id', 'apps', ['id'], unique=False)

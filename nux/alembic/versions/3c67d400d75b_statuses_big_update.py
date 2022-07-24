"""statuses big update

Revision ID: 3c67d400d75b
Revises: a88ad21d28bd
Create Date: 2022-07-22 20:43:37.220780

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3c67d400d75b'
down_revision = 'a88ad21d28bd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'user_statuses_v2',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('app_id', sa.String(), nullable=True),
        sa.Column('dt_last_update', sa.DateTime(), nullable=False),
        sa.Column('dt_entered_app', sa.DateTime(), nullable=True),
        sa.Column('dt_leaved_app', sa.DateTime(), nullable=True),
        sa.Column('in_app', sa.Boolean(), nullable=False),
        sa.Column('online', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['app_id'], ['apps.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_statuses_v2_id'),
                    'user_statuses_v2', ['id'], unique=False)
    op.drop_index('ix_user_statuses_id', table_name='user_statuses')
    op.drop_table('user_statuses')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'user_statuses',
        sa.Column('id', sa.VARCHAR(),
                  autoincrement=False, nullable=False),
        sa.Column('user_id', sa.VARCHAR(),
                  autoincrement=False, nullable=True),
        sa.Column('current_app_id', sa.VARCHAR(),
                  autoincrement=False, nullable=True),
        sa.Column('last_update', postgresql.TIMESTAMP(),
                  autoincrement=False, nullable=False),
        sa.Column('started_at', postgresql.TIMESTAMP(),
                  autoincrement=False, nullable=False),
        sa.Column('finished', sa.BOOLEAN(),
                  autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['current_app_id'], [
            'apps.id'], name='user_statuses_current_app_id_fkey'),
        sa.ForeignKeyConstraint(
            ['user_id'], ['users.id'], name='user_statuses_user_id_fkey'),
        sa.PrimaryKeyConstraint('id', name='user_statuses_pkey')
    )
    op.create_index('ix_user_statuses_id',
                    'user_statuses', ['id'], unique=False)
    op.drop_index(op.f('ix_user_statuses_v2_id'),
                  table_name='user_statuses_v2')
    op.drop_table('user_statuses_v2')
    # ### end Alembic commands ###

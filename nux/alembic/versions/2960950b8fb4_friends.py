"""Friends

Revision ID: 2960950b8fb4
Revises: 0b43488d8aa4
Create Date: 2022-08-09 11:44:49.084194

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2960950b8fb4'
down_revision = '0b43488d8aa4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'friends_invites',
        sa.Column('from_user_id', sa.String(), nullable=False),
        sa.Column('to_user_id', sa.String(), nullable=False),
        sa.Column('dt_sent', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['from_user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['to_user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('from_user_id', 'to_user_id')
    )
    op.create_table(
        'friendships',
        sa.Column('user1_id', sa.String(), nullable=False),
        sa.Column('user2_id', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['user1_id'], ['users.id']),
        sa.ForeignKeyConstraint(['user2_id'], ['users.id']),
        sa.PrimaryKeyConstraint('user1_id', 'user2_id')
    )


def downgrade() -> None:
    op.drop_table('friendships')
    op.drop_table('friends_invites')

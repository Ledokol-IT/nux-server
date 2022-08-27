"""new apps

Revision ID: 8439ef1ee4b3
Revises: 4707aa768df3
Create Date: 2022-08-27 18:45:56.347627

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.sql
from sqlalchemy.sql import column
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8439ef1ee4b3'
down_revision = '4707aa768df3'
branch_labels = None
depends_on = None


def generate_approved_game(id, android_package_name, name):
    return {
        "id": str(id),
        "android_package_name": android_package_name,
        "name": name,
        "category": "GAME,online",
        "approved": True,
    }


first_approved_apps = [
    {
        "name": "CarX Drift Racing 2",
        "android_package_name": "com.carxtech.carxdr2",
    },
    {
        "name": "Hide Online",
        "android_package_name": "com.hitrock.hideonline",
    },
    {
        "name": "Ninja Turtles: Legends",
        "android_package_name": "com.ludia.tmnt",
    },
    {
        "name": "Ark of War",
        "android_package_name": "com.sevenpirates.infinitywar",
    },
    {
        "name": "War and Magic",
        "android_package_name": "com.stgl.global",
    },
    {
        "name": "Last Day on Earth",
        "android_package_name": "zombie.survival.craft.z",
    },
    {
        "name": "Soul Knight",
        "android_package_name": "com.ChillyRoom.DungeonShooter",
    },
    {
        "name": "AFK Arena",
        "android_package_name": "com.lilithgame.hgame.gp",
    },
    {
        "name": "Triviador",
        "android_package_name": "com.thxgames.triviador",
    },
    {
        "name": "Chess.com",
        "android_package_name": "com.chess",
    },
    {
        "name": "Mobile Legends: Bang Bang",
        "android_package_name": "com.mobile.legends",
    },
    {
        "name": "World of Tanks Blitz",
        "android_package_name": "net.wargaming.wot.blitz",
    },
    {
        "name": "Танки Онлайн",
        "android_package_name": "com.tankionline.mobile.production",
    },
]


def upgrade() -> None:
    op.alter_column(
        'apps', 'category',
        existing_type=postgresql.ENUM(
            'GAME', 'OTHER', name='category'),
        type_=sa.String(),
        existing_nullable=False,
    )
    return
    apps_table = sqlalchemy.sql.table(
        'apps',
        column("id", sa.String),
        column("android_package_name", sa.String),
        column("name", sa.String),
        column("category", sa.String),
        column("icon_preview", sa.String),
        column("image_wide", sa.String),
        column("icon_large", sa.String),
        column("approved", sa.Boolean),
    )
    op.bulk_insert(
        apps_table,
        [generate_approved_game(i, a["android_package_name"], a["name"])
            for i, a in enumerate(first_approved_apps, 1)]
    )


def downgrade() -> None:
    op.alter_column(
        'apps', 'category',
        existing_type=sa.String(),
        type_=postgresql.ENUM('GAME', 'OTHER', name='category'),
        existing_nullable=False,
    )

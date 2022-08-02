"""approved apps

Revision ID: 61c1fad8f21a
Revises: fccc925ee9a4
Create Date: 2022-07-26 11:21:21.018846

"""
import enum
import uuid

from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg_types
import sqlalchemy.sql
from sqlalchemy.sql import column, table


# revision identifiers, used by Alembic.
revision = '61c1fad8f21a'
down_revision = 'fccc925ee9a4'
branch_labels = None
depends_on = None


def generate_approved_game(id, android_package_name, name):
    s3_url = 'https://storage.yandexcloud.net/nux'
    return {
        "id": str(id),
        "android_package_name": android_package_name,
        "name": name,
        "category": "GAME",
        "icon_preview": '/'.join([
            s3_url,
            "icons",
            "icon_preview",
            android_package_name,
        ]) + ".png",
        "icon_large": '/'.join([
            s3_url,
            "icons",
            "icon_large",
            android_package_name,
        ]) + ".png",
        "image_wide": '/'.join([
            s3_url,
            "icons",
            "image_wide",
            android_package_name,
        ]) + ".png",
        "approved": True,
    }


first_approved_apps = [
    {
        "name": "Call of Duty",
        "android_package_name": "com.activision.callofduty.shooter",
    },
    {
        "name": "Among Us",
        "android_package_name": "com.innersloth.spacemafia",
    },
    {
        "name": "Brawl Stars",
        "android_package_name": "com.supercell.brawlstars",
    },
    {
        "name": "PUBG",
        "android_package_name": "com.tencent.ig",
    },
    {
        "name": "Clash of Clans",
        "android_package_name": "com.supercell.clashofclans",
    },
    {
        "name": "FIFA",
        "android_package_name": "com.ea.gp.fifamobile",
    },
    {
        "name": "Roblox",
        "android_package_name": "com.roblox.client",
    },
    {
        "name": "Clash Royale",
        "android_package_name": "com.supercell.clashroyale",
    },
    {
        "name": "Standoff 2",
        "android_package_name": "com.axlebolt.standoff2",
    },
    {
        "name": "Дурак Онлайн",
        "android_package_name": "com.rstgames.durak",
    },
    {
        "name": "Genshin Impact",
        "android_package_name": "com.miHoYo.GenshinImpact",
    },
    {
        "name": "Hearthstone",
        "android_package_name": "com.blizzard.wtcg.hearthstone",
    },
]


class CATEGORY(enum.Enum):
    GAME = "GAME"
    OTHER = "OTHER"


def upgrade() -> None:
    op.execute("DELETE FROM user_in_app_statistics")
    op.execute("DELETE FROM user_statuses_v2")
    op.execute("DELETE FROM apps")
    op.add_column('apps', sa.Column(
        'approved',
        sa.Boolean(),
        server_default='FALSE',
        nullable=False,
    ))
    apps_table = sqlalchemy.sql.table(
        'apps',
        column("id", sa.String),
        column("android_package_name", sa.String),
        column("name", sa.String),
        column("category", pg_types.ENUM(CATEGORY)),
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
    op.drop_column('apps', 'approved')

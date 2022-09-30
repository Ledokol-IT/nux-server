"""remove icons

Revision ID: ada1332b86e7
Revises: 8439ef1ee4b3
Create Date: 2022-09-30 09:40:27.982255

"""
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base


# revision identifiers, used by Alembic.
revision = 'ada1332b86e7'
down_revision = '8439ef1ee4b3'
branch_labels = None
depends_on = None

Base = declarative_base()


class App(Base):
    __tablename__ = "apps"

    id: str = sa.Column(
        sa.String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )  # type: ignore

    android_package_name: str | None = sa.Column(
        sa.String,
        unique=True,
        nullable=True,  # maybe we will support other os
    )  # type: ignore
    icon_preview: str | None = sa.Column(
        sa.String,
        nullable=True,
    )  # type: ignore


new_approved_apps = [
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
    bind = op.get_bind()
    session = orm.Session(bind=bind, autoflush=False)
    for app_data in new_approved_apps:
        app = session.query(
            App
        ).filter(
            App.android_package_name == app_data["android_package_name"]
        ).first()
        if app is None:
            print(f"{app_data['android_package_name']} not found!")
            return
        app.icon_preview = None
    session.commit()


def downgrade() -> None:
    pass

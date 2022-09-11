"""new apps

Revision ID: 8439ef1ee4b3
Revises: 4707aa768df3
Create Date: 2022-08-27 18:45:56.347627

"""
import uuid
import typing as t

from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy.sql
from sqlalchemy.sql import column

Base = declarative_base()

# revision identifiers, used by Alembic.
revision = '8439ef1ee4b3'
down_revision = '4707aa768df3'
branch_labels = None
depends_on = None

CATEGORY = t.Literal["GAME", "GAME,online", "OTHER"]


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
    name: str = sa.Column(
        sa.String,
        nullable=True,
    )  # type: ignore
    category: CATEGORY = sa.Column(
        sa.String,
        nullable=False,
    )  # type: ignore
    icon_preview: str | None = sa.Column(
        sa.String,
        nullable=True,
    )  # type: ignore
    image_wide: str | None = sa.Column(
        sa.String,
        nullable=True,
    )  # type: ignore
    icon_large: str | None = sa.Column(
        sa.String,
        nullable=True,
    )  # type: ignore

    approved: bool = sa.Column(
        sa.Boolean,
        nullable=False,
        server_default="FALSE",
    )  # type: ignore


def generate_approved_game(id, android_package_name, name):
    app = App()
    app.id = str(id)
    app.android_package_name = android_package_name
    app.name = name
    app.category = "GAME,online"
    app.approved = True
    return app


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
    op.alter_column(
        'apps', 'category',
        existing_type=postgresql.ENUM(
            'GAME', 'OTHER', name='category'),
        type_=sa.String(),
        existing_nullable=False,
    )
    op.execute('ALTER TABLE apps ALTER COLUMN category TYPE text')
    bind = op.get_bind()
    session = orm.Session(bind=bind)
    print("123")

    approved_apps = session.query(App).where(App.approved).all()
    for app in approved_apps:
        app.category = "GAME,online"
    initial_id = 13
    for id, app_data in enumerate(new_approved_apps, initial_id):
        app = generate_approved_game(id, **app_data)
        old_app = session.query(
            App
        ).where(App.android_package_name == app.android_package_name).first()
        if old_app:
            session.delete(old_app)
        session.add(app)

    session.commit()


def downgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind)
    # create the teams table and the players.team_id column
    # App.__table__.create(bind)

    approved_apps = session.query(App).where(
        App.category == "GAME,online").all()
    for app in approved_apps:
        app.category = "GAME"

    session.commit()
    op.execute('ALTER TABLE apps ALTER COLUMN category TYPE category'
               ' USING category::category')

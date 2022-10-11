from __future__ import annotations
import typing as t
import uuid

import sqlalchemy as sa
import sqlalchemy.orm as orm

import nux.database
import nux.models.user as muser
from nux.schemes import AppSchemeCreateAndroid, AppScheme


class UserInAppStatistic(nux.database.Base):
    __tablename__ = "user_in_app_statistics"
    user_id: str = sa.Column(
        sa.String,
        sa.ForeignKey("users.id"),
        primary_key=True,
    )  # type: ignore
    user: 'muser.User' = orm.relationship(
        lambda: muser.User,
        back_populates="apps_stats"
    )

    app_id: str = sa.Column(
        sa.String,
        sa.ForeignKey("apps.id"),
        primary_key=True,
    )  # type: ignore
    app: 'App' = orm.relationship(lambda: App)


class App(nux.database.Base):
    __tablename__ = "apps"

    id: str = sa.Column(
        sa.String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )  # type: ignore

    @staticmethod
    def _generate_id():
        return str(uuid.uuid4())

    android_package_name: str | None = sa.Column(
        sa.String,
        unique=True,
        nullable=True,  # maybe we will support other os
    )  # type: ignore
    name: str = sa.Column(
        sa.String,
        nullable=True,
    )  # type: ignore
    category: str = sa.Column(
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

    def is_visible(self):
        return "GAME" in self.category


def create_app_android(app_data: AppSchemeCreateAndroid):
    app = App()
    app.id = App._generate_id()
    app.android_package_name = app_data.android_package_name
    app.name = app_data.name
    app.approved = False

    match_category: dict[t.Any, str] = {
        None: "OTHER",
        0: "GAME",
    }
    if app_data.android_category in match_category:
        app.category = match_category[app_data.android_category]
    else:
        app.category = "OTHER"
    return app


def determine_app_android(
        session: orm.Session,
        app_data: AppSchemeCreateAndroid
) -> tuple[bool, App]:
    """
    Return `(True, new_app)` if no mathed app is found,
    returns `(False, found_app)` otherwise.
    App is added to session, but not commited
    """
    app = session.query(App).filter(
        App.android_package_name == app_data.android_package_name
    ).first()
    if app is not None:
        return False, app

    app = create_app_android(app_data)
    session.add(app)
    return True, app


def add_app_to_user(
        session: orm.Session,
        user: 'muser.User',
        app: App,
):
    app_stats = UserInAppStatistic()
    app_stats.app = app
    app_stats.user = user
    session.add(app_stats)


def delete_app_from_user(
        session: orm.Session,
        user: 'muser.User',
        app: App,
):
    app_stats = session.query(UserInAppStatistic).get({
        "user_id": user.id,
        "app_id": app.id,
    })
    if app_stats is None:
        return
    session.delete(app_stats)


def get_user_apps(
        session: orm.Session,
        user: 'muser.User',
        *,
        only_visible: bool = False,
        only_approved: bool = False,
        only_games: bool = False,
        only_online: bool = False,
) -> list[App]:
    q = (
        session.query(App)
        .join(UserInAppStatistic)
        .where(UserInAppStatistic.user_id == user.id)
    )
    if only_visible:
        only_games = True
    if only_approved:
        q = q.where(App.approved)
    if only_games:
        q = q.where(App.category.contains('GAME'))  # type: ignore
    if only_online:
        q = q.where(App.category.contains('online'))  # type: ignore

    return q.all()


def set_apps_to_user(
        session: orm.Session,
        user: 'muser.User',
        apps: t.Iterable[App],
):
    user_apps = set(get_user_apps(session, user))
    apps = set(apps)
    to_add = apps.difference(user_apps)
    to_delete = user_apps.difference(apps)
    for app in to_add:
        add_app_to_user(session, user, app)
    for app in to_delete:
        delete_app_from_user(session, user, app)


def get_app(
        session: orm.Session,
        id: str | None = None, android_package_name: str | None = None
) -> App | None:
    cnt_args = sum(map(lambda x: x is not None, [id, android_package_name]))
    if cnt_args != 1:
        raise ValueError(f"Expected 1 argument. Find {cnt_args}")

    query = session.query(App)
    app = None
    if id is not None:
        app = query.get(id)
    elif android_package_name is not None:
        app = query.filter(App.android_package_name
                           == android_package_name).first()
    return app

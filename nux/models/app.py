import enum
import uuid
from typing import Iterable

import pydantic
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg_types
import sqlalchemy.orm as orm

import nux.database
import nux.models.user


class UserInAppStatistic(nux.database.Base):
    __tablename__ = "user_in_app_statistics"
    user_id: str = sa.Column(
        sa.String,
        sa.ForeignKey("users.id"),
        primary_key=True,
    )  # type: ignore
    user: 'nux.models.user.User' = orm.relationship(
        lambda: nux.models.user.User,
        back_populates="apps_stats"
    )

    app_id: str = sa.Column(
        sa.String,
        sa.ForeignKey("apps.id"),
        primary_key=True,
    )  # type: ignore
    app: 'App' = orm.relationship(lambda: App)


class CATEGORY(enum.Enum):
    GAME = "GAME"
    OTHER = "OTHER"


class App(nux.database.Base):
    __tablename__ = "apps"

    DEFAULT_ICON_PREVIEW = "https://storage.yandexcloud.net/nux/icons/common/preview_icon.png"  # noqa
    DEFAULT_ICON_LARGE = "https://storage.yandexcloud.net/nux/icons/common/large_icon.png"  # noqa
    DEFAULT_ICON_WIDE = "https://storage.yandexcloud.net/nux/icons/common/wide_icon.png"  # noqa

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
        pg_types.ENUM(CATEGORY),
        nullable=False,
        default=CATEGORY.OTHER,
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


class AppSchemeBase(pydantic.BaseModel):
    android_package_name: str | None
    name: str


class AppSchemeCreateAndroid(AppSchemeBase):
    android_package_name: str
    android_category: int | None


class AppScheme(AppSchemeBase):
    category: CATEGORY
    id: str
    icon_preview: str | None
    image_wide: str | None
    icon_large: str | None

    @pydantic.validator("icon_preview", pre=True, check_fields=False)
    def set_default_app_icon_preview(cls, value):
        return value or App.DEFAULT_ICON_PREVIEW

    @pydantic.validator("icon_large", pre=True, check_fields=False)
    def set_default_app_icon_large(cls, value):
        return value or App.DEFAULT_ICON_LARGE

    @pydantic.validator("icon_wide", pre=True, check_fields=False)
    def set_default_app_icon_wide(cls, value):
        return value or App.DEFAULT_ICON_WIDE

    class Config:
        orm_mode = True


def create_app_android(app_data: AppSchemeCreateAndroid):
    app = App()
    app.android_package_name = app_data.android_package_name
    app.name = app_data.name

    match_category = {
        None: CATEGORY.OTHER,
        0: CATEGORY.GAME,
    }
    if app_data.android_category in match_category:
        app.category = match_category[app_data.android_category]
    else:
        app.category = CATEGORY.OTHER
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
        user: 'nux.models.user.User',
        app: App,
):
    app_stats = UserInAppStatistic()
    app_stats.app = app
    app_stats.user = user
    session.add(app_stats)


def delete_app_from_user(
        session: orm.Session,
        user: 'nux.models.user.User',
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
        user: 'nux.models.user.User',
        approved: bool = True,
) -> list[App]:
    q = (
        session.query(App)
        .join(UserInAppStatistic)
        .where(UserInAppStatistic.user_id == user.id)
    )
    if approved:
        q = q.where(App.approved)
    return q.all()


def set_apps_to_user(
        session: orm.Session,
        user: 'nux.models.user.User',
        apps: Iterable[App],
):
    user_apps = set(get_user_apps(session, user, approved=False))
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
        app = query.filter(App.android_package_name ==
                           android_package_name).first()
    return app

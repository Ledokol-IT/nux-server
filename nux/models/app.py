import uuid
import enum

import pydantic
import sqlalchemy as sa
import sqlalchemy.orm as orm
import sqlalchemy.dialects.postgresql as pg_types

import nux.database
import nux.models.user


class UserInAppStatistic(nux.database.Base):
    __tablename__ = "user_in_app_statistics"
    user_id: str = sa.Column(
        sa.String,
        sa.ForeignKey("users.id"),
        primary_key=True,
    )  # type: ignore
    _user: 'nux.models.user.User' = orm.relationship(
        lambda: nux.models.user.User,
        back_populates="apps_stats"
    )

    app_id: str = sa.Column(
        sa.String,
        sa.ForeignKey("apps.id"),
        primary_key=True,
    )  # type: ignore
    # app: 'App' = orm.relationship(lambda: App)


class CATEGORY(enum.Enum):
    GAME = "GAME"
    OTHER = "OTHER"


class App(nux.database.Base):
    __tablename__ = "apps"

    id: str = sa.Column(
        sa.String,
        primary_key=True,
        index=True,
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
    android_category: str | None = sa.Column(
        sa.String,
        nullable=True,
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


class AppSchemeBase(pydantic.BaseModel):
    android_package_name: str | None
    name: str


class AppSchemeCreateAndroid(AppSchemeBase):
    android_package_name: str
    android_category: str | None


class AppScheme(AppSchemeBase):
    category: CATEGORY
    id: str
    icon_preview: str | None
    image_wide: str | None
    icon_large: str | None

    class Config:
        orm_mode = True


def create_app_android(app_data: AppSchemeCreateAndroid):
    app = App()
    app.android_package_name = app_data.android_package_name
    app.name = app_data.name
    app.android_category = app_data.android_category

    match_category = {
        None: CATEGORY.OTHER,
        "CATEGORY_GAME": CATEGORY.GAME,
    }
    if app_data.android_category in match_category:
        app.category = match_category[app_data.android_category]
    else:
        app.category = CATEGORY.OTHER
    return app


def determine_app_android(session: orm.Session, app_data: AppSchemeCreateAndroid) -> tuple[bool, App]:
    """
    Return `(True, new_app)` if no mathed app is found, returns `(False, found_app)` otherwise.
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

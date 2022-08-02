import datetime
import typing as t
import uuid

import pydantic
import sqlalchemy as sa
import sqlalchemy.orm as orm

import nux.database
import nux.models.user
import nux.models.app
import nux.events
from nux.utils import now


class UserStatus(nux.database.Base):
    __tablename__ = "user_statuses_v2"

    id: str = sa.Column(
        sa.String,
        primary_key=True,
        index=True,
        default=lambda: str(uuid.uuid4())
    )  # type: ignore

    user_id: str = sa.Column(
        sa.String,
        sa.ForeignKey("users.id"),
    )  # type: ignore
    _user: 'nux.models.user.User' = orm.relationship(
        lambda: nux.models.user.User,
        back_populates="status",
    )

    app_id: str = sa.Column(
        sa.String,
        sa.ForeignKey("apps.id"),
        nullable=True,
    )  # type: ignore
    app: nux.models.app.App | None = orm.relationship(
        lambda: nux.models.app.App)

    dt_last_update: datetime.datetime = sa.Column(
        sa.DateTime,
        nullable=False,
    )  # type: ignore
    dt_entered_app: datetime.datetime | None = sa.Column(
        sa.DateTime,
        nullable=True,
    )  # type: ignore
    dt_leaved_app: datetime.datetime | None = sa.Column(
        sa.DateTime,
        nullable=True,
    )  # type: ignore
    in_app: bool = sa.Column(
        sa.Boolean,
        nullable=False,
        default=False,
    )  # type: ignore
    online: bool = sa.Column(
        'online',
        sa.Boolean,
        nullable=False,
        default=False,
    )  # type: ignore

    ONLINE_TTL = datetime.timedelta(seconds=30)


class UserStatusSchemeSecure(pydantic.BaseModel):
    id: str
    app: t.Optional['nux.models.app.AppScheme']
    dt_last_update: datetime.datetime
    dt_entered_app: datetime.datetime | None
    dt_leaved_app: datetime.datetime | None
    in_app: bool
    online: bool

    class Config:
        orm_mode = True


class UserStatusScheme(UserStatusSchemeSecure):
    pass


def create_empty_status():
    status = UserStatus()
    status.app = None
    status.dt_last_update = now()
    status.dt_entered_app = None
    status.dt_leaved_app = None
    status.in_app = False
    status.online = True

    return status


def update_status_in_app(
    session: orm.Session,
    user: 'nux.models.user.User',
    app: 'nux.models.app.App',
    events: 'nux.events.NuxEvents',
):
    if (
            user.status is not None
            and user.status.in_app
            and user.status.app == app
    ):
        user.status.dt_last_update = now()
    elif app.category == nux.models.app.CATEGORY.OTHER:
        update_status_not_in_app(session, user)
    else:
        status = create_empty_status()
        status.app = app
        status.dt_entered_app = now()
        status.dt_leaved_app = None
        status.in_app = True
        user.status = status

        events.user_entered_app(session, user, app)
    return user.status


def status_leave_app(status: UserStatus):
    if status.in_app:
        status.in_app = False
        status.dt_leaved_app = now()


def update_status_not_in_app(
    session: orm.Session,
    user: 'nux.models.user.User'
):
    if user.status is None:
        user.status = create_empty_status()
        return user.status

    user.status.dt_last_update = now()
    user.status.online = True
    status_leave_app(user.status)
    return user.status


def clear_offline_users_by_ttl(session: orm.Session) -> None:
    min_online_time = now() - UserStatus.ONLINE_TTL
    statuses = (
        session.query(UserStatus)
        .where(UserStatus.online)
        .where(UserStatus.dt_last_update < min_online_time)
        .all()
    )
    for status in statuses:
        status_leave_app(status)
        status.dt_last_update = now()
        status.online = False

import datetime
import typing as t
import uuid

import pydantic
import sqlalchemy as sa
import sqlalchemy.orm as orm

import nux.database
import nux.models.user
import nux.models.app


class UserStatus(nux.database.Base):
    __tablename__ = "user_statuses"

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

    current_app_id: str = sa.Column(
        sa.String,
        sa.ForeignKey("apps.id"),
        nullable=True,
    )  # type: ignore
    current_app: nux.models.app.App | None = orm.relationship(
        lambda: nux.models.app.App)

    last_update: datetime.datetime = sa.Column(
        sa.DateTime,
        nullable=False,
    )  # type: ignore
    started_at: datetime.datetime = sa.Column(
        sa.DateTime,
        nullable=False,
    )  # type: ignore

    finished: bool = sa.Column(
        sa.Boolean,
        nullable=False,
    )  # type: ignore


class UserStatusSchemeBase(pydantic.BaseModel):
    last_update: datetime.datetime
    started_at: datetime.datetime
    finished: bool
    pass


class UserStatusSchemeSecure(UserStatusSchemeBase):
    id: str
    current_app: t.Optional['nux.models.app.AppScheme']

    class Config:
        orm_mode = True


class UserStatusScheme(UserStatusSchemeSecure):
    pass


def create_empty_status():
    new_status = UserStatus()
    new_status.last_update = new_status.started_at = datetime.datetime.now()
    new_status.finished = True
    return new_status


def update_status_in_app(session: orm.Session, user: 'nux.models.user.User', app: 'nux.models.app.App'):
    if user.status is not None and user.status.current_app == app:
        user.status.last_update = datetime.datetime.utcnow()
        session.merge(user.status)
    else:
        new_status = UserStatus()
        new_status.current_app = app
        new_status.last_update = new_status.started_at = datetime.datetime.now()
        new_status.finished = False
        user.status = new_status
        session.merge(user)
    return user.status


def update_status_leave_app(session: orm.Session, user: 'nux.models.user.User'):
    if user.status is None:
        return None
    else:
        user.status.finished = True
    session.merge(user.status)
    return user.status

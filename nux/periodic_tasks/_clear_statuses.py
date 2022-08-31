from __future__ import annotations
import datetime
import logging

import sqlalchemy as sa
from sqlalchemy import orm

import nux.config
import nux.database
import nux.models.status
import nux.models.status as mstatus
import nux.models.user as muser
import nux.notifications
from nux.utils import now

logger = logging.getLogger(__name__)


class OfflineUser(nux.database.Base):
    __tablename__ = "offline_users"

    user_id: str = sa.Column(
        sa.String,
        sa.ForeignKey("users.id"),
        primary_key=True,
    )  # type: ignore

    dt_next_ping: datetime.datetime = sa.Column(
        sa.DateTime,
        nullable=False,
    )  # type: ignore
    pinged_cnt: int = sa.Column(
        sa.Integer,
        nullable=False,
    )  # type: ignore

    def get_dt_next_ping(self):
        initial_interval = datetime.timedelta(seconds=20)
        max_interval = datetime.timedelta(hours=7)
        if self.pinged_cnt > 10:
            interval = max_interval
        else:
            interval = min(max_interval, initial_interval *
                           2 ** self.pinged_cnt)
        return self.dt_next_ping + interval


def reset_offline_user(session: orm.Session, user_id: str):
    o = session.query(OfflineUser).get(user_id)
    if o is None:
        o = OfflineUser()
    o.user_id = user_id
    o.dt_next_ping = now()
    o.pinged_cnt = 0
    session.add(o)


def clear_statuses():
    with nux.database.Session() as session:
        min_online_time = now() - mstatus.UserStatus.ONLINE_TTL
        statuses = (
            session.query(mstatus.UserStatus)
            .where(mstatus.UserStatus.online)
            .where(mstatus.UserStatus.dt_last_update < min_online_time)
            .all()
        )

        for status in statuses:
            if status.user_id is None:
                session.delete(status)
                continue
            mstatus.status_leave_app(status)
            status.dt_last_update = now()
            status.online = False

            logger.debug(f"turn offline {status._user!r}")
            reset_offline_user(session, status.user_id)

        session.commit()


def ping_users():
    with nux.database.Session() as session:
        users_and_offline = (
            session.query(muser.User, OfflineUser)
            .join(OfflineUser)
            .where(OfflineUser.dt_next_ping < now())
        ).all()
        users = []
        for user, offline in users_and_offline:
            if user.status.online:
                session.delete(offline)
                continue

            logger.debug(f"ping {user!r}")
            offline.dt_next_ping = offline.get_dt_next_ping()
            offline.pinged_cnt += 1

            users.append(user)

        session.commit()

        nux.notifications.send_ping(session, users)

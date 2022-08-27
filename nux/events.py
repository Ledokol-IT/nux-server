from __future__ import annotations

import fastapi
import sqlalchemy.orm

import nux.notifications


class NuxEvents:
    def __init__(self, background_tasks: fastapi.BackgroundTasks):
        self.background_tasks = background_tasks

    def user_entered_app(
        self,
        session: sqlalchemy.orm.Session,
        user: 'muser.User',
        app: 'mapp.App',
    ):
        self.background_tasks.add_task(
            nux.notifications.send_notification_user_entered_app,
            session, user, app)

    def friends_invite(
        self,
        session: sqlalchemy.orm.Session,
        from_user: muser.User,
        to_user: muser.User,
    ):
        self.background_tasks.add_task(
            nux.notifications.send_notification_friends_inivite,
            session, from_user, to_user)

    def accept_friends_invite(
        self,
        session: sqlalchemy.orm.Session,
        from_user: muser.User,
        to_user: muser.User,
    ):
        self.background_tasks.add_task(
            nux.notifications.send_notification_accept_friends_invite,
            session, from_user, to_user)


def EventsDependecy() -> NuxEvents:
    return fastapi.Depends(NuxEvents)


__all__ = (
    "NuxEvents",
    "EventsDependecy",
)

import nux.models.user as muser
import nux.models.app as mapp

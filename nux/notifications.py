from __future__ import annotations
import logging
import uuid

import firebase_admin.messaging
import pydantic
import sqlalchemy.orm

import nux.database
import nux.events
import nux.firebase
from nux.schemes import AppN, UserN

logger = logging.getLogger(__name__)


_Value = str | pydantic.BaseModel | dict[str, '_Value'] | None


def _encode_dict(
        d: dict[str, str],
        prefix: str,
        v: _Value
):
    match v:
        case str():
            d[prefix] = v
        case pydantic.BaseModel():
            _encode_dict(d, prefix, v.dict())
        case dict():
            if prefix:
                prefix = prefix + '.'
            for key, value in v.items():
                _encode_dict(d, prefix + key, value)
        case None:
            pass


def encode_message(*, type: str, **kwargs: _Value):
    message = {}
    message["type"] = type
    message["id"] = str(uuid.uuid4())
    _encode_dict(message, '', kwargs)
    return message


def is_user_ready_to_notification(user: nux.models.user.User) -> bool:
    if not user.firebase_messaging_token:
        return False
    if user.do_not_disturb:
        return False
    return True


def _make_message_user_entered_app(
    from_user: 'nux.models.user.User',
    app: 'nux.models.app.App',
    to_user: 'nux.models.user.User',
):
    """
    user -- user joined the app
    friend -- user to notify
    """
    if not is_user_ready_to_notification(to_user):
        return None
    data = encode_message(
        type="friend_entered_app",
        user=UserN.from_orm(from_user),
        app=AppN.from_orm(app),
    )
    return firebase_admin.messaging.Message(
        data=data,
        token=to_user.firebase_messaging_token,
    )


def send_notification_user_entered_app(
    session: sqlalchemy.orm.Session,
    user: 'nux.models.user.User',
    app: 'nux.models.app.App'
):
    logger.debug(f"{user.nickname} entered the {app.android_package_name}")
    if not app.is_visible():
        return
    if nux.firebase.firebase_app is None:
        return

    friends = mfriends.get_friends(session, user)
    none_or_messages = (
        _make_message_user_entered_app(user, app, friend) for friend in friends
    )
    messages = [m for m in none_or_messages if m is not None]
    nux.firebase.send_messages(messages)


def send_notification_friends_inivite(
    session: sqlalchemy.orm.Session,
    from_user: 'nux.models.user.User',
    to_user: 'nux.models.user.User',
):
    _ = session

    logger.debug(f"{from_user!r} invited {to_user!r}")

    if not is_user_ready_to_notification(to_user):
        return None

    from_user_n = UserN.from_orm(from_user)
    data = encode_message(
        type="friends_invite",
        from_user=from_user_n,
    )
    message = firebase_admin.messaging.Message(
        data=data,
        token=to_user.firebase_messaging_token,
    )
    nux.firebase.send_message(message)


def send_notification_accept_friends_invite(
    session: sqlalchemy.orm.Session,
    from_user: 'nux.models.user.User',
    to_user: 'nux.models.user.User',
):
    _ = session

    logger.debug(f"{from_user!r} accepted {to_user!r}")

    if not is_user_ready_to_notification(to_user):
        return None

    from_user_n = UserN.from_orm(from_user)
    data = encode_message(
        type="accept_friends_invite",
        from_user=from_user_n,
    )
    message = firebase_admin.messaging.Message(
        data=data,
        token=to_user.firebase_messaging_token,
    )
    nux.firebase.send_message(message)


def _make_message_invite_to_app(
    from_user: 'nux.models.user.User',
    to_user: 'nux.models.user.User',
    app: 'nux.models.app.App',
):
    if not is_user_ready_to_notification(to_user):
        return None
    data = encode_message(
        type="invite_to_app",
        user=UserN.from_orm(from_user),
        app=AppN.from_orm(app),
    )

    return firebase_admin.messaging.Message(
        data=data,
        token=to_user.firebase_messaging_token,
    )


def send_invite_to_app_from_friend(
    session: sqlalchemy.orm.Session,
    from_user: 'nux.models.user.User',
    to_users: list['nux.models.user.User'],
    app: 'nux.models.app.App',
):
    _ = session
    if nux.firebase.firebase_app is None:
        return

    none_or_messages = (
        _make_message_invite_to_app(
            from_user,
            friend,
            app
        ) for friend in to_users
    )
    messages = [m for m in none_or_messages if m is not None]
    nux.firebase.send_messages(messages)


def _make_message_ping(
    to_user: 'nux.models.user.User',
):
    if not is_user_ready_to_notification(to_user):
        return None
    data = encode_message(
        type="ping",
    )
    logger.debug(f"data ping {data}")

    return firebase_admin.messaging.Message(
        data=data,
        token=to_user.firebase_messaging_token,
    )


def send_ping(
        session: sqlalchemy.orm.Session,
        to_users: list['nux.models.user.User'],
):
    _ = session
    if nux.firebase.firebase_app is None:
        return
    logger.debug(f"Ping {to_users}")

    none_or_messages = (
        _make_message_ping(
            user
        ) for user in to_users
    )
    messages = [m for m in none_or_messages if m is not None]
    logger.debug(messages)
    nux.firebase.send_messages(messages)


import nux.models.app
import nux.models.friends as mfriends
import nux.models.user

import logging
import fastapi.encoders
import firebase_admin.messaging
import sqlalchemy.orm

import nux.database
import nux.events
import nux.firebase
import nux.models.app
import nux.models.user
import nux.models.friends as mfriends

_is_setted_up = False


def setup_notifications(options):
    global _is_setted_up
    if _is_setted_up:
        return
    _is_setted_up = True
    _ = options
    nux.events.user_entered_app.on(send_notification_user_entered_app)


logger = logging.getLogger(__name__)


def is_user_ready_to_notification(user: nux.models.user.User) -> bool:
    if not user.firebase_messaging_token:
        return False
    if user.do_not_disturb:
        return False
    return True


def make_message_user_entered_app(
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
    data = {
        "type": "friend_entered_app",
        "user_nickname": from_user.nickname,
        "user_id": from_user.id,
        "app_name": app.name,
        "app_id": app.id,
        "app_android_package_name": app.android_package_name,
        "app_icon_preview": app.icon_preview,
    }
    data = fastapi.encoders.jsonable_encoder(data)
    # firebase accept only strings as values
    data = {key: str(data[key]) for key in data if data[key] is not None}
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
    if nux.firebase.firebase_app is None:
        return

    friends = mfriends.get_friends(session, user)
    none_or_messages = (
        make_message_user_entered_app(user, app, friend) for friend in friends
    )
    messages = [m for m in none_or_messages if m is not None]
    nux.firebase.send_messages(messages)


def make_message_invite_to_app(
    from_user: 'nux.models.user.User',
    to_user: 'nux.models.user.User',
    app: 'nux.models.app.App',
):
    """
    user -- user joined the app
    friend -- user to notify
    """
    if not is_user_ready_to_notification(to_user):
        return None
    data = {
        "type": "invite_to_app",
        "user_nickname": from_user.nickname,
        "user_id": from_user.id,
        "app_name": app.name,
        "app_id": app.id,
        "app_android_package_name": app.android_package_name,
        "app_icon_preview": app.icon_preview,
    }
    data = fastapi.encoders.jsonable_encoder(data)
    # firebase accept only strings as values
    data = {key: str(data[key]) for key in data if data[key] is not None}

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
        make_message_invite_to_app(
            from_user,
            friend,
            app
        ) for friend in to_users
    )
    messages = [m for m in none_or_messages if m is not None]
    nux.firebase.send_messages(messages)

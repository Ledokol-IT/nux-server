import fastapi.encoders
import firebase_admin.messaging
import pydantic

import nux.database
import nux.events
import nux.firebase
import nux.models.app
import nux.models.user


def setup_notifications(options):
    nux.events.user_entered_app.on(send_notification_user_entered_app)


def make_message_user_entered_app(
    from_user: 'nux.models.user.User',
    app: 'nux.models.app.App',
    to_user: 'nux.models.user.User',
):
    """
    user -- user joined the app
    friend -- user to notify
    """
    if not to_user.firebase_messaging_token:
        return None
    data = {
        "message_type": "friend_entered_app",
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
    user: 'nux.models.user.User',
    app: 'nux.models.app.App'
):
    if nux.firebase.firebase_app is None:
        return

    with nux.database.Session() as session:
        friends = nux.models.user.get_friends(session, user)
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
    if not to_user.firebase_messaging_token:
        return None
    data = {
        "message_type": "invite_to_app",
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
    from_user: 'nux.models.user.User',
    to_user: 'nux.models.user.User',
    app: 'nux.models.app.App',
):
    if nux.firebase.firebase_app is None:
        return

    with nux.database.Session() as session:
        message = make_message_invite_to_app(from_user, to_user, app)
        if message is not None:
            nux.firebase.send_message(message)

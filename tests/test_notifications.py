import unittest.mock

import pytest

from tests.utils import create_user, get_user, make_friends
from tests.utils import app1_android_payload
import nux.notifications


def set_token(client, user):
    FIREBASE_TOKEN = "eVjN_YclQVeNyB2Q6-2Z7I:APA91bFBafO_bPKvBJhrUx_y20fmbokAq3ISv7npx-kuQhQpgaxgifLGJ8K919ZVzu4Ns7ZH02gZC5F-8MUSZni9KRMMeQKUBhhLR6M6XMMKQ3F3bbyzMfg09CqM53RWJrOInzEVXU92"  # noqa

    client.put(
        "/current_user/firebase_messaging_token",
        json={
            "firebase_messaging_token": FIREBASE_TOKEN,
        },
        headers=user,
    )


@pytest.fixture
def friend_id(client, friend_with_token_auth):
    response = client.get("/current_user", headers=friend_with_token_auth)
    return response.json()["id"]


@unittest.mock.patch("nux.firebase.send_messages")
def test_notifications_sent_then_user_entered_app_and_leaved(
        patched_firebase_send_messages,
        client,
):
    patched_firebase_send_messages.assert_not_called()
    user = create_user(client)
    friend = create_user(client)
    make_friends(client, user, friend)
    set_token(client, friend)

    response = client.put(
        "/status/in_app/android",
        json={
            "app": app1_android_payload,
        },
        headers=user,
    )
    assert response.status_code == 200
    patched_firebase_send_messages.assert_called_once()

    patched_firebase_send_messages.reset_mock()

    response = client.put(
        "/status/not_in_app",
        headers=user,
    )
    assert response.status_code == 200
    patched_firebase_send_messages.assert_called_once()


@unittest.mock.patch("nux.firebase.send_messages")
def test_invite(
        patched_firebase_send_messages: unittest.mock.Mock,
        client,
        user_auth_header,
        sync_app1
):
    user = user_auth_header
    friend = create_user(client)
    make_friends(client, user, friend)
    set_token(client, friend)
    friend_id = get_user(client, friend)["id"]
    response = client.post(
        "/friends/invite",
        json={
            "app_id": sync_app1["id"],
            "friends_ids": [friend_id],
        },
        headers=user,
    )
    assert response.status_code == 200
    patched_firebase_send_messages.assert_called_once()
    assert len(patched_firebase_send_messages.call_args[0]) == 1


def test_encode_message():
    app = nux.notifications.AppN(
        id="app_id",
        name="app_name",
        icon_preview="app_icon_preview",
        android_package_name="app_android_package_name"
    )
    user = nux.notifications.UserN(
        id="user_id",
        nickname="user_nickname",
        name="user_name",
        profile_pic="123",
    )
    message = nux.notifications.encode_message(
        type="test",
        app=app,
        user=user,
    )
    expected_message = {
        "app.id": "app_id",
        "app.name": "app_name",
        "app.icon_preview": "app_icon_preview",
        "app.android_package_name": "app_android_package_name",
        "user.id": "user_id",
        "user.nickname": "user_nickname",
        "user.name": "user_name",
        "user.profile_pic": "123",
        "type": "test",
    }
    assert "id" in message
    del message["id"]
    assert expected_message == message

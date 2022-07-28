import pytest
import tests.utils


@pytest.fixture
def friend_with_token_auth(client):
    FIREBASE_TOKEN = "eVjN_YclQVeNyB2Q6-2Z7I:APA91bFBafO_bPKvBJhrUx_y20fmbokAq3ISv7npx-kuQhQpgaxgifLGJ8K919ZVzu4Ns7ZH02gZC5F-8MUSZni9KRMMeQKUBhhLR6M6XMMKQ3F3bbyzMfg09CqM53RWJrOInzEVXU92"  # noqa
    friend_auth = tests.utils.create_user(client, "friend")

    client.put(
        "/current_user/firebase_messaging_token",
        json={
            "firebase_messaging_token": FIREBASE_TOKEN,
        },
        headers=friend_auth,
    )
    return friend_auth


@pytest.fixture
def friend_id(client, friend_with_token_auth):
    response = client.get("/get_me", headers=friend_with_token_auth)
    return response.json()["id"]


def test_notifications_sent_then_user_entered_app(
    client,
    user_auth_header,
    friend_with_token_auth
):
    response = client.put(
        "/status/in_app/android",
        json={
            "app": tests.utils.app1_android_payload,
        },
        headers=user_auth_header,
    )
    assert response.status_code == 200


def test_invite(client, user_auth_header, friend_id, sync_app1):
    response = client.post(
        "/friends/invite",
        json={
            "app_id": sync_app1["id"],
            "friends_ids": [friend_id],
        },
        headers=user_auth_header,
    )
    assert response.status_code == 200

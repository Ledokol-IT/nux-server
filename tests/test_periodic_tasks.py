import unittest.mock

import freezegun

from nux.periodic_tasks._clear_statuses import clear_statuses, ping_users
from tests.utils import app1_android_payload


@unittest.mock.patch("nux.firebase.send_messages")
def test_clear_status_ok(
        patched_firebase_send_messages: unittest.mock.Mock,
        client,
        user_auth_header
):
    with freezegun.freeze_time("2012-01-14 12:00"):
        response = client.put(
            "/status/in_app/android",
            json={
                "app": app1_android_payload,
            },
            headers=user_auth_header,
        )
        assert response.status_code == 200

    with freezegun.freeze_time("2012-01-14 12:03"):
        clear_statuses()

    response = client.get(
        "/current_user",
        headers=user_auth_header,
    )
    assert response.json()["status"]["online"] is False

    patched_firebase_send_messages.reset_mock()
    with freezegun.freeze_time("2012-01-14 12:05"):
        ping_users()
    patched_firebase_send_messages.assert_called_once()
    assert len(patched_firebase_send_messages.call_args[0]) == 1


def test_clear_status_momentaly(client, user_auth_header):
    response = client.put(
        "/status/in_app/android",
        json={
            "app": app1_android_payload,
        },
        headers=user_auth_header,
    )
    assert response.status_code == 200

    clear_statuses()

    response = client.get(
        "/current_user",
        headers=user_auth_header,
    )
    assert response.json()["status"]["online"] is True

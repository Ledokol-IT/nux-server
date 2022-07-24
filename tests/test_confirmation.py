import pytest
import unittest.mock
import nux.confirmation


@unittest.mock.patch("nux.sms.send_confirmation_code")
def test_post_phone_confirmation(patched_send_confirmation_code, client):
    phone = "+79069469277"
    response = client.post(
        '/confirmation/phone',
        json={
            "phone": phone,
            "reason": "registration",
        },
    )
    assert response.status_code == 200
    patched_send_confirmation_code.assert_called_once()
    assert patched_send_confirmation_code.call_args.args[0] == phone


@unittest.mock.patch("nux.sms.send_confirmation_code")
def test_phone_confirmation_check(
        patched_send_confirmation_code,
        client,
        session
):
    phone = "+79069469277"
    response = client.post(
        '/confirmation/phone',
        json={
            "phone": phone,
            "reason": "registration",
        },
    )
    assert response.status_code == 200
    patched_send_confirmation_code.assert_called_once()

    code = patched_send_confirmation_code.call_args.args[1]
    id = response.json()["id"]

    assert nux.confirmation.check_phone_confirmation(
        session,
        id,
        phone,
        code,
        'registration',
    )


@unittest.mock.patch("nux.sms.send_confirmation_code")
def test_phone_confirmation_check_bad_code(
        patched_send_confirmation_code,
        client,
        session
):
    phone = "+79069469277"
    response = client.post(
        '/confirmation/phone',
        json={
            "phone": phone,
            "reason": "registration",
        },
    )
    assert response.status_code == 200
    patched_send_confirmation_code.assert_called_once()

    id = response.json()["id"]

    assert not nux.confirmation.check_phone_confirmation(
        session,
        id,
        phone,
        "0000",
        'registration',
    )


@unittest.mock.patch("nux.sms.send_confirmation_code")
def test_phone_confirmation_check_bad_phone(
        patched_send_confirmation_code,
        client,
        session
):
    phone = "+79069469277"
    response = client.post(
        '/confirmation/phone',
        json={
            "phone": phone,
            "reason": "registration",
        },
    )
    assert response.status_code == 200
    patched_send_confirmation_code.assert_called_once()

    code = patched_send_confirmation_code.call_args.args[1]
    id = response.json()["id"]

    assert not nux.confirmation.check_phone_confirmation(
        session,
        id,
        "+79009009000",
        code,
        'registration',
    )

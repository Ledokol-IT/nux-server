import pytest
from tests.utils import get_phone_confirmation, create_user


def test_registration_ok(client):
    phone = "+79009009000"
    response = client.post(
        "/register",
        json={
            "user": {
                "phone": phone,
                "nickname": "nickname",
                "name": "A name"
            },
            "phone_confirmation": get_phone_confirmation(
                client, phone, 'registration'),
        },
    )
    assert response.status_code == 200
    assert 'access_token' in response.json()


def test_login_phone_ok(client):
    phone = "+79009009000"
    create_user(client, phone=phone)
    response = client.post(
        "/login",
        json={
            "phone": phone,
            "phone_confirmation": get_phone_confirmation(
                client, phone, 'login'),
        },
    )

    assert response.status_code == 200
    assert 'access_token' in response.json()


@pytest.mark.skip("doesn't implement registration with password only")
def test_login_ok(client):
    good_register_payload = {}
    response = client.post(
        "/register",
        json=good_register_payload,
    )
    assert response.status_code == 200

    response = client.post(
        "/token",
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data=f"grant_type=&"
        f"username={good_register_payload['nickname']}&"
        f"password={good_register_payload['password']}&"
        f"scope=&client_id=&client_secret=",
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.skip("doesn't implement registration with password only")
def test_login_bad_password(client):
    good_register_payload = {}
    response = client.post(
        "/register",
        json=good_register_payload,
    )
    assert response.status_code == 200

    response = client.post(
        "/token",
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data=f"grant_type=&"
        f"username={good_register_payload['nickname']}&"
        f"password=badPwd&"
        f"scope=&client_id=&client_secret=",
    )
    assert response.status_code == 401

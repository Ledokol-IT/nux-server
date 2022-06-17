import pytest


good_register_payload = {
    "nickname": "test_nickname",
    "password": "fakeGoodPassword!",
}


def test_registration_ok(client):
    response = client.post(
        "/register",
        json=good_register_payload,
    )
    assert response.status_code == 200
    assert 'access_token' in response.json()


def test_login_ok(client):
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


def test_login_bad_password(client):
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

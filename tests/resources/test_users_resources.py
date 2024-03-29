from tests.utils import create_user


def test_get_current_user(client, user_auth_header):
    response = client.get("/current_user", headers=user_auth_header)
    assert response.status_code == 200

    assert "nickname" in response.json()


def test_default_pic(client, user_auth_header):
    response = client.get("/current_user", headers=user_auth_header)
    assert response.status_code == 200

    assert response.json()["profile_pic"] is not None


def test_get_user_by_id(client):
    user_auth = create_user(client, nickname="mommy")
    user = client.get("/current_user", headers=user_auth).json()
    response = client.get(f"/user/{user['id']}")
    assert response.status_code == 200
    assert response.json()["nickname"] == "mommy"


def test_get_user_non_exist(client):
    response = client.get("/user/xxxx")
    assert response.status_code == 404


def test_get_user_by_phone(client):
    phone = "+79009009000"
    nickname = "test_nick"
    create_user(client, phone=phone, nickname=nickname)
    response = client.get("/users", params={
        "phone": phone,
    })
    assert response.status_code == 200
    assert response.json()["nickname"] == nickname


def test_get_user_by_nickname(client):
    create_user(client, nickname="test_nick")
    response = client.get("/users/?nickname=test_nick")
    assert response.status_code == 200
    assert response.json()["nickname"] == "test_nick"


def test_check_user_by_phone_existing(client):
    phone = "+79009009000"
    create_user(client, phone=phone)
    response = client.get("/users/check", params={
        "phone": phone,
    })
    assert response.status_code == 200
    assert response.json()["exists"] is True


def test_check_user_by_phone_non_existing(client):
    phone = "+79009009000"
    response = client.get("/users/check", params={
        "phone": phone,
    })
    assert response.status_code == 200
    assert response.json()["exists"] is False


def test_do_not_disturb_false_by_default(client, user_auth_header):
    response = client.get("/current_user",
                          headers=user_auth_header)
    assert response.json()["do_not_disturb"] is False


def test_do_not_disturb_set_to_true(client, user_auth_header):
    response = client.put(
        "/current_user/do_not_disturb",
        json={
            "do_not_disturb": True,
        },
        headers=user_auth_header
    )
    assert response.status_code == 200
    response = client.get("/current_user",
                          headers=user_auth_header)
    assert response.json()["do_not_disturb"] is True


def test_change_user(client, user_auth_header):
    response = client.put(
        "/current_user/edit",
        headers=user_auth_header,
        json={
            "user": {
                "nickname": "changed_nickname",
            }
        }
    )
    assert response.status_code == 200

    assert "nickname" in response.json()
    assert response.json()["nickname"] == "changed_nickname"

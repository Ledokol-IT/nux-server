from tests.utils import create_user


def test_get_me(client, user_auth_header):
    response = client.get("/get_me", headers=user_auth_header)
    assert response.status_code == 200

    assert "nickname" in response.json()


def test_get_user_by_nickname(client):
    create_user(client, "mommy")
    response = client.get("/user/mommy")
    assert response.status_code == 200
    assert response.json()["nickname"] == "mommy"


# def test_get_friends(client, user_auth_header):
#     create_user(client, "good_friend")
#
#     response = client.get("/friends", headers=user_auth_header)
#     assert response.status_code == 200
#
#     data = response.json()
#     assert len(data) > 0
#     assert "nickname" in data[0]
#     assert data[0]["nickname"] == "good_friend"
#     assert "status" in data[0]# 

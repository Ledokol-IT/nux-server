import unittest.mock
import time

from tests.utils import create_user, get_user, set_token

from tests.utils import make_friends


@unittest.mock.patch("nux.firebase.send_message")
def test_make_friends(
        patched_firebase_send_messages,
        client
):
    start_time = time.time()
    pref = "make_friends__"
    user1_nickname = pref + "user1"
    user1 = create_user(client, nickname=user1_nickname)
    user1_id = get_user(client, user1)["id"]
    set_token(client, user1)
    user2_nickname = pref + "user2"
    user2 = create_user(client, nickname=user2_nickname)
    user2_id = get_user(client, user2)["id"]
    set_token(client, user2)

    # empty at creation
    res = client.get("/friends/pending_invites", headers=user1)
    assert res.status_code == 200
    assert len(res.json()) == 0

    res = client.get("/friends/outgoing_invites", headers=user1)
    assert res.status_code == 200
    assert len(res.json()) == 0

    res = client.get("/friends", headers=user1)
    assert res.status_code == 200
    assert len(res.json()) == 0

    # pending invite
    res = client.put(
        "/friends/add",
        json={"user_id": user2_id},
        headers=user1,
    )
    patched_firebase_send_messages.assert_called_once()
    assert res.status_code == 200
    res = client.get("/friends/pending_invites", headers=user2)
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["from_user"]["id"] == user1_id

    res = client.get("/friends/outgoing_invites", headers=user1)
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["to_user"]["id"] == user2_id

    res = client.get("/friends", headers=user2)
    assert len(res.json()) == 0

    # Friends!!!
    patched_firebase_send_messages.reset_mock()
    res = client.put(
        "/friends/add",
        json={"user_id": user1_id},
        headers=user2,
    )
    patched_firebase_send_messages.assert_called_once()
    res = client.get("/friends/pending_invites", headers=user2)
    assert res.status_code == 200
    assert len(res.json()) == 0

    res = client.get("/friends/outgoing_invites", headers=user1)
    assert res.status_code == 200
    assert len(res.json()) == 0

    res = client.get("/friends", headers=user2)
    assert len(res.json()) == 1
    assert res.json()[0]["id"] == user1_id
    end_time = time.time()
    print(end_time - start_time)


def test_remove_friends(client):
    user1 = create_user(client)
    user2 = create_user(client)
    make_friends(client, user1, user2)
    user2_id = get_user(client, user2)["id"]

    response = client.delete(
        "/friends/remove_friend",
        params={
            "friend_id": user2_id
        },
        headers=user1,
    )
    assert response.status_code == 200

    res = client.get("/friends/pending_invites", headers=user2)
    assert res.status_code == 200
    assert len(res.json()) == 0

    res = client.get("/friends/outgoing_invites", headers=user1)
    assert res.status_code == 200
    assert len(res.json()) == 0

    res = client.get("/friends", headers=user2)
    assert len(res.json()) == 0


def test_reject_invite(client):
    user1 = create_user(client)
    user2 = create_user(client)
    user1_id = get_user(client, user1)["id"]
    user2_id = get_user(client, user2)["id"]

    res = client.put(
        "/friends/add",
        json={"user_id": user2_id},
        headers=user1,
    )

    res = client.delete(
        "/friends/reject_invite",
        params={
            "from_user_id": user1_id
        },
        headers=user2,
    )
    assert res.status_code == 200

    res = client.get("/friends/pending_invites", headers=user2)
    assert res.status_code == 200
    assert len(res.json()) == 0

    res = client.get("/friends/outgoing_invites", headers=user1)
    assert res.status_code == 200
    assert len(res.json()) == 0

    res = client.get("/friends", headers=user2)
    assert len(res.json()) == 0


def test_remove_invite(client):
    user1 = create_user(client)
    user2 = create_user(client)
    user2_id = get_user(client, user2)["id"]

    res = client.put(
        "/friends/add",
        json={"user_id": user2_id},
        headers=user1,
    )

    res = client.delete(
        "/friends/remove_invite",
        params={
            "to_user_id": user2_id
        },
        headers=user1,
    )
    assert res.status_code == 200

    res = client.get("/friends/pending_invites", headers=user2)
    assert res.status_code == 200
    assert len(res.json()) == 0

    res = client.get("/friends/outgoing_invites", headers=user1)
    assert res.status_code == 200
    assert len(res.json()) == 0

    res = client.get("/friends", headers=user2)
    assert len(res.json()) == 0


def test_recommended_friends(client):
    user1 = create_user(client)
    user2 = create_user(client)
    user3 = create_user(client)
    make_friends(client, user1, user2)
    make_friends(client, user2, user3)
    user3_id = get_user(client, user3)["id"]

    res = client.get("/friends/recommended", headers=user1)
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["id"] == user3_id


def test_is_friend(client):
    user1 = create_user(client)
    user2 = create_user(client)
    user2_id = get_user(client, user2)["id"]
    make_friends(client, user1, user2)

    res = client.get(
        f"/friends/user/{user2_id}/is_friend",
        headers=user1,
    )
    assert res.status_code == 200
    assert res.json() is True


def test_is_friend_false(client):
    user1 = create_user(client)
    user2 = create_user(client)
    user2_id = get_user(client, user2)["id"]

    res = client.get(
        f"/friends/user/{user2_id}/is_friend",
        headers=user1,
    )
    assert res.status_code == 200
    assert res.json() is False

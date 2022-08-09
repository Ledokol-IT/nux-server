from tests.utils import create_user, get_user


def test_make_friends(client):
    pref = "make_friends__"
    user1_nickname = pref + "user1"
    user1 = create_user(client, nickname=user1_nickname)
    user1_id = get_user(client, user1)["id"]
    user2_nickname = pref + "user2"
    user2 = create_user(client, nickname=user2_nickname)
    user2_id = get_user(client, user2)["id"]

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
    res = client.put(
        "/friends/add",
        json={"user_id": user1_id},
        headers=user2,
    )
    res = client.get("/friends/pending_invites", headers=user2)
    assert res.status_code == 200
    assert len(res.json()) == 0

    res = client.get("/friends/outgoing_invites", headers=user1)
    assert res.status_code == 200
    assert len(res.json()) == 0

    res = client.get("/friends", headers=user2)
    assert len(res.json()) == 1
    assert res.json()[0]["id"] == user1_id

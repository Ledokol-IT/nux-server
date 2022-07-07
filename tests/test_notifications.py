import tests.utils


def test_notifications_send(client, user_auth_header):
    FIREBASE_TOKEN = "fqgwT92wTKS7iDLAuABSYT:APA91bGJUy4Ud3NF-AUm3Z14JRTZQYKXRYs5BT3NFXTfSflamABbDwYlFReStUtypAfoFIQfCC0ichGES4bFN9yNQDVxvAyW96miQwQ3aaPKCfDJWquGGTb8i8FmOh4Z9kxGVXGrmlQM"
    friend_auth = tests.utils.create_user(client, "friend")

    response = client.put(
        "/current_user/firebase_messaging_token",
        json={
            "firebase_messaging_token": FIREBASE_TOKEN,
        },
        headers=user_auth_header,
    )
    assert response.status_code == 200

    response = client.put(
        "/status/set/android",
        json={
            "app": tests.utils.app1_android_payload,
        },
        headers=friend_auth,
    )
    assert response.status_code == 200

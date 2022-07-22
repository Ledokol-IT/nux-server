from tests.utils import app1_android_payload


def test_set_status_ok(client, user_auth_header):
    response = client.put(
        "/status/in_app/android",
        json={
            "app": app1_android_payload,
        },
        headers=user_auth_header,
    )
    assert response.status_code == 200
    data = response.json()
    response_app = data["app"]
    assert response_app["android_package_name"] == app1_android_payload["android_package_name"]
    assert data["in_app"] == True


def test_set_and_get_status(client, user_auth_header):
    response = client.put(
        "/status/in_app/android",
        json={
            "app": app1_android_payload,
        },
        headers=user_auth_header,
    )
    assert response.status_code == 200

    response = client.get(
        "/get_me",
        headers=user_auth_header,
    )
    assert response.json()[
        "status"]["app"]["android_package_name"] == app1_android_payload["android_package_name"]


def test_set_and_unset_status(client, user_auth_header):
    response = client.put(
        "/status/in_app/android",
        json={
            "app": app1_android_payload,
        },
        headers=user_auth_header,
    )
    assert response.status_code == 200

    response = client.put(
        "/status/not_in_app",
        headers=user_auth_header,
    )
    assert response.status_code == 200
    assert response.json()["in_app"] == False


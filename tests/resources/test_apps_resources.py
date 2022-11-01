import faker

from nux.schemes import AppSchemeCreateAndroid
from tests.utils import get_user, make_friends, create_user, sync_apps_with_user
from pprint import pprint

fake = faker.Faker()


def create_android_app_payload(
    package_name: str | None = None,
    category: int | None = None,
    name: str | None = None,
):
    if package_name is None:
        package_name = fake.domain_name(levels=4)
    if category is None:
        category = fake.random_element(elements=[
            0,
            None,
        ])
    if name is None:
        name = fake.company()
    return {
        "android_package_name": package_name,
        "android_category": category,
        "name": name,
    }


def test_sync_apps_ok(client, user_auth_header):
    faker.Faker.seed(0)

    apps = [create_android_app_payload() for _ in range(5)]

    response = client.put(
        "/sync_installed_apps/android",
        json={
            "apps": apps,
        },
        headers=user_auth_header,
    )
    assert response.status_code == 200
    data = response.json()
    assert "apps" in data


def test_get_approved_app_ok(client):
    response = client.get(f"/app/1")
    assert response.status_code == 200
    expected_package_name = "com.activision.callofduty.shooter"
    assert response.json()["android_package_name"] == expected_package_name


def test_get_apps(client, sync_app1, user_auth_header):
    user = get_user(client, user_auth_header)
    response = client.get(f"/user/{user['id']}/apps")
    assert response.status_code == 200
    assert response.json()["apps"][0]["android_package_name"] \
        == sync_app1["android_package_name"]


def test_recommended_apps(client):
    user1 = create_user(client)
    user2 = create_user(client)
    user3 = create_user(client)
    user4 = create_user(client)
    make_friends(client, user1, user2)
    make_friends(client, user1, user3)
    make_friends(client, user3, user4)
    app1 = create_android_app_payload(category=0)
    app2 = create_android_app_payload(category=0)
    app3 = create_android_app_payload(category=0)
    app4 = create_android_app_payload(category=0)
    sync_apps_with_user(client, user1, [app1])
    sync_apps_with_user(client, user2, [app2, app3])
    sync_apps_with_user(client, user3, [app1, app3])
    sync_apps_with_user(client, user4, [app4])
    res = client.get("/apps/recommendations", headers=user1)
    assert res.status_code == 200
    pprint(res.json())
    pprint({"apps": [app3, app2]})
    assert len(res.json()["apps"]) == 2
    assert all(x["android_package_name"] == y["android_package_name"] for x, y in zip(res.json()["apps"], (app3, app2)))

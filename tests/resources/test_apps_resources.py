import faker

from tests.utils import get_user

fake = faker.Faker()


def create_android_app_payload(
    package_name: str | None = None,
    category: str | None = None,
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

import faker

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
            "CATEGORY_GAME",
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
    apps_response = data["apps"]
    assert len(apps_response) == len(apps)


def test_get_app_ok(client, sync_app1):
    response = client.get(f"/app/{sync_app1['id']}")
    assert response.status_code == 200
    assert response.json()["android_package_name"] == sync_app1["android_package_name"]

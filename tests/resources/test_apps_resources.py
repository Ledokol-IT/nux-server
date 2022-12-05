import logging

import faker
import freezegun
from datetime import timedelta as td
from nux.utils import now

from tests.utils import get_user, make_friends, create_user,\
    sync_apps_with_user, create_android_app_payload

fake = faker.Faker()


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
    assert len(res.json()["apps"]) == 2
    assert all(x["android_package_name"] == y["android_package_name"]
               for x, y in zip(res.json()["apps"], [app3, app2]))


def test_update_statistics(client):
    faker.Faker.seed(0)
    user = create_user(client)
    apps = [create_android_app_payload(category=0) for _ in range(5)]
    sync_apps_with_user(client, user, apps)
    local_records = []
    total_need = td(seconds=0)
    with freezegun.freeze_time("2012-01-14 12:00"):
        for i, app in enumerate(apps):
            dt_begin = now() - td(days=(i + 1) * 2, hours=12)
            dt_end = now() - td(days=(i + 1))
            total_need += dt_end - dt_begin
            local_records.append({
                "android_package_name": app["android_package_name"],
                "dt_begin": dt_begin.isoformat(timespec='seconds'),
                "dt_end": dt_end.isoformat(timespec='seconds'),
            })
        res = client.put("/apps/statistics/update_from_local/android",
                         json={"local_records": local_records}, headers=user)
        assert res.status_code == 200
        res = client.get("/apps/current_user/v2", headers=user)
        assert res.status_code == 200
        apps_and_stats = res.json()["apps_and_stats"]
        total = td(seconds=sum(x["statistics"]["activity_total"]
                               for x in apps_and_stats))
        assert total == total_need

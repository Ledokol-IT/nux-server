import string
from typing import Union
import unittest.mock
import random
import faker

fake = faker.Faker()
random.seed(0)


def create_user_token(
    client,
    nickname: str | None = None,
    phone: str | None = None,
):
    nickname = nickname or ''.join(
        random.choices(string.ascii_lowercase, k=10))
    phone = phone or '+7900' + ''.join(
        random.choices(string.digits, k=7))
    payload = {
        "user": {
            "nickname": nickname,
            "password": "fakeGoodPassword!",
            "name": nickname.capitalize(),
            "phone": phone,
        },
        "phone_confirmation": get_phone_confirmation(
            client, phone, 'registration'),
    }
    response = client.post(
        "/register",
        json=payload,
    )
    return response.json()["access_token"]


def create_user(
    client,
    *,
    nickname: str | None = None,
    phone: str | None = None,
):
    return {
        "Authorization": f'Bearer {create_user_token(client, nickname, phone)}'
    }


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


def get_user(client, headers):
    return client.get("/current_user", headers=headers).json()


def make_friends(client, user1, user2):
    user1_id = get_user(client, user1)["id"]
    user2_id = get_user(client, user2)["id"]
    client.put(
        "/friends/add",
        json={"user_id": user2_id},
        headers=user1,
    )
    client.put(
        "/friends/add",
        json={"user_id": user1_id},
        headers=user2,
    )


def set_token(client, user):
    FIREBASE_TOKEN = "eVjN_YclQVeNyB2Q6-2Z7I:APA91bFBafO_bPKvBJhrUx_y20fmbokAq3ISv7npx-kuQhQpgaxgifLGJ8K919ZVzu4Ns7ZH02gZC5F-8MUSZni9KRMMeQKUBhhLR6M6XMMKQ3F3bbyzMfg09CqM53RWJrOInzEVXU92"  # noqa

    client.put(
        "/current_user/firebase_messaging_token",
        json={
            "firebase_messaging_token": FIREBASE_TOKEN,
        },
        headers=user,
    )


app1_android_payload = {
    "name": "Call of Duty",
    "android_package_name": "com.activision.callofduty.shooter",
    "android_category": 0,
}


@unittest.mock.patch("nux.sms.send_confirmation_code")
def get_phone_confirmation(
        client,
        phone,
        reason,
        patched_send_confirmation_code
):
    response = client.post(
        '/confirmation/phone',
        json={
            "phone": phone,
            "reason": reason,
        },
    )

    id = response.json()["id"]
    code = patched_send_confirmation_code.call_args.args[1]
    return {
        "code": code,
        "id": id,
    }


def sync_apps_with_user(client, user_auth_header, apps):
    client.put(
        "/sync_installed_apps/android",
        json={
            "apps": apps,
        },
        headers=user_auth_header,
    )

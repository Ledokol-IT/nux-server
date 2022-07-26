import string
from typing import Union
import unittest.mock
import random


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
    nickname: str | None = None,
    phone: str | None = None,
):
    return {
        "Authorization": f'Bearer {create_user_token(client, nickname, phone)}'
    }


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

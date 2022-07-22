from typing import Union


def create_user_token(client, nickname: str, phone: Union[str, None]=None):
    payload = {
        "nickname": nickname,
        "password": "fakeGoodPassword!",
        "name": nickname.capitalize(),
        "phone": phone
    }
    response = client.post(
        "/register",
        json=payload,
    )
    return response.json()["access_token"]


def create_user(client, nickname: str, phone: Union[str, None]=None):
    return {
        "Authorization": f'Bearer {create_user_token(client, nickname, phone)}'
    }


app1_android_payload = {
    "name": "123 Good App",
    "android_package_name": "com.example.good_app",
    "android_category": 0,
}

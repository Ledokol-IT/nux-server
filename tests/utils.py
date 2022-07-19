def create_user_token(client, nickname: str):
    payload = {
        "nickname": nickname,
        "password": "fakeGoodPassword!",
        "name": nickname.capitalize(),
    }
    response = client.post(
        "/register",
        json=payload,
    )
    return response.json()["access_token"]


def create_user(client, nickname: str):
    return {
        "Authorization": f'Bearer {create_user_token(client, nickname)}'
    }


app1_android_payload = {
    "name": "123 Good App",
    "android_package_name": "com.example.good_app",
    "android_category": 0,
}

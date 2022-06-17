def create_user(client, nickname):
    payload = {
        "nickname": nickname,
        "password": "fakeGoodPassword!",
    }
    client.post(
        "/register",
        json=payload,
    )
    return nickname


app1_android_payload = {
    "name": "Good App",
    "android_package_name": "com.example.good_app",
    "android_category": "CATEGORY_GAME",
}

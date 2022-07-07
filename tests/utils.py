def create_user(client, nickname):
    payload = {
        "nickname": nickname,
        "password": "fakeGoodPassword!",
    }
    response = client.post(
        "/register",
        json=payload,
    )
    return {"Authorization": f'Bearer {response.json()["access_token"]}'}


app1_android_payload = {
    "name": "Good App",
    "android_package_name": "com.example.good_app",
    "android_category": "CATEGORY_GAME",
}

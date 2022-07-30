def test_default_profile_pics_list(client):
    response = client.get("/default_profile_pics/list")
    assert response.status_code == 200
    pics_list = response.json()["default_profile_pics"]
    assert len(pics_list) > 0
    assert "id" in pics_list[0]
    assert "url" in pics_list[0]

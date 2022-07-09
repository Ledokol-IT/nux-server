import uuid

import fastapi
import fastapi.testclient
import pytest
import sqlalchemy.exc
import sqlalchemy_utils

from nux import create_app
import nux.config
import nux.database
from tests.utils import app1_android_payload, create_user_token, create_user


@pytest.fixture
def app():
    tmp_db = '.'.join([uuid.uuid4().hex, 'pytest'])
    args = [
        "--pg-user", "web",
        "--pg-password", "pass",
        "--pg-db", tmp_db,
        "--pg-host", "localhost:5432",
        "--secret-key", "123",
        # "--firebase-dry-run",
        "--google-creds", "./ledokol-it-google-auth.json"
    ]
    options = nux.config.parse_args(args)
    sqlalchemy_utils.create_database(options.postgres_url)

    nux.database.create_all(options)
    app = create_app(options)
    try:
        yield app
    finally:
        try:
            sqlalchemy_utils.drop_database(options.postgres_url)
        except sqlalchemy.exc.ProgrammingError:
            pass


@pytest.fixture
def client(app):
    with fastapi.testclient.TestClient(app) as c:
        yield c


@pytest.fixture
def user_auth_header(client):
    return create_user(client, "main_test_user")


@pytest.fixture
def sync_app1(client, user_auth_header):
    response = client.put(
        "/sync_installed_apps/android",
        json={
            "apps": [app1_android_payload],
        },
        headers=user_auth_header,
    )
    return response.json()["apps"][0]


@pytest.fixture
def second_user(client):
    good_register_payload = {
        "nickname": "second_user",
        "password": "fakeGoodPassword2!",
    }
    response = client.post(
        "/register",
        json=good_register_payload,
    )
    return response.json()["access_token"]

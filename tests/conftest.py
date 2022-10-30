import uuid

import fastapi
import fastapi.testclient
import pytest
import sqlalchemy.exc
import sqlalchemy_utils

from nux.app import create_app
import nux.config
import nux.database
from tests.utils import app1_android_payload, create_user_token, create_user


@pytest.fixture
def session(app):
    return nux.database.Session()


@pytest.fixture
def session_factory(app):
    return nux.database.Session


@pytest.fixture
def options():
    tmp_db = '.'.join([uuid.uuid4().hex, 'pytest'])
    args = [
        "--pg-db", tmp_db,
        "--secret-key", "123",
        "--firebase-dry-run",
        "--sms-disable",
        "--aws-disable",
        "--aws-access-key-id", "YCAJEjQ6RldyNLfUtBaMUJZWQ",
        "--aws-secret-access-key", "YCPM8_Qc-Bf_gDKfFq3ct2b2GxQPZcJnhq7U0GR8",
    ]
    options = nux.config.parse_args(args)
    return options


@pytest.fixture
def app(options):
    sqlalchemy_utils.create_database(options.postgres_url)

    # nux.database.create_all(options.postgres_url)
    nux.database.run_migrations(options.postgres_url)
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
    return create_user(client, nickname="main_test_user")


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

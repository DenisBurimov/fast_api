from typing import Generator

import pytest
from fastapi.testclient import TestClient
from pymongo.database import Database

from app import schema as s
from tests.fixture import TestData


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    from app.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture
def authorized_users_tokens(
    client: TestClient,
    db: Database,
    test_data: TestData,
) -> Generator[list[s.Tokens], None, None]:
    tokens = []
    for user in test_data.test_authorized_users:
        response = client.post(
            "api/auth/login",
            data={
                "username": user.email,
                "password": user.password,
            },
        )

        assert response and response.status_code == 200
        login_response = s.Tokens.parse_obj(response.json())
        tokens += [login_response.access_token]
    yield tokens


@pytest.fixture
def client_a(
    client: TestClient,
    db: Database,
    test_data: TestData,
):
    user = test_data.test_users[0]
    response = client.post(
        "api/auth/login",
        data={
            "username": user.email,
            "password": user.password,
        },
    )

    assert response and response.status_code == 200
    login_response = s.Tokens.parse_obj(response.json())
    client.headers["Authorization"] = f"Bearer {login_response.access_token}"
    yield client

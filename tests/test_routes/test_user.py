from fastapi.testclient import TestClient
from pymongo.database import Database
import app.schema as s
from tests.fixture import TestData


def test_auth(client: TestClient, db: Database, test_data: TestData):
    request_data = s.UserLogin(
        username=test_data.test_users[0].username,
        password=test_data.test_users[0].password,
    )
    # login by username and password
    response = client.post("api/auth/login", data=request_data.dict())
    assert response and response.status_code == 200, "unexpected response"


def test_signup(client: TestClient, db: Database, test_data: TestData):
    request_data = s.User(
        username=test_data.test_user.username,
        email=test_data.test_user.email,
        password=test_data.test_user.password,
    )
    response = client.post("api/auth/sign-up", json=request_data.dict())
    assert response and response.status_code == 201
    assert db.users.find_one({"email": test_data.test_user.email})


def test_get_all_users(client: TestClient, db: Database, test_data: TestData):
    response = client.get("api/user/all")
    assert response and response.status_code == 200


def test_get_user_by_id(client: TestClient, db: Database, test_data: TestData):
    test_user = db.users.find_one()

    test_user_id = str(test_user.get("id"))
    test_user_username = test_user.get("username")
    test_user_email = test_user.get("email")
    response = client.get(f"api/user/{test_user_id}")
    assert response and response.status_code == 200
    assert test_user_username in response.text
    assert test_user_email in response.text


def test_update_user(client: TestClient, db: Database, test_data: TestData):
    test_user = db.users.find_one()

    test_user_id = str(test_user.get("id"))
    data = s.UserUpdate(
        username="New Username",
        email=test_user.get("email"),
        password_hash=test_user.get("password_hash"),
    ).dict()
    response = client.put(f"api/user/{test_user_id}", json=data)
    assert response and response.status_code == 200
    user = s.UserDB.parse_raw(response.text)
    assert str(user.id) == test_user_id


def test_delete_user(client: TestClient, db: Database, test_data: TestData):
    test_user = db.users.find_one()
    users_number_before = len(list(db.users.find()))

    test_user_id = str(test_user.get("id"))
    response = client.delete(f"api/user/{test_user_id}")
    assert response and response.status_code == 200

    users_number_after = len(list(db.users.find()))
    assert users_number_before > users_number_after

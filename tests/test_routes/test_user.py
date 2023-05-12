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
    response = client.get(f"api/user/{test_user_id}")
    assert response and response.status_code == 200

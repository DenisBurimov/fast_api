from fastapi.testclient import TestClient
from pymongo.database import Database
import app.schema as s
from tests.fixture import TestData


def test_auth(client: TestClient, db: Database, test_data: TestData):
    response = client.post(
        "api/auth/login",
        data=s.UserLogin(
            username=test_data.test_users[0].name,
            password=test_data.test_users[0].password,
        ).dict(),
    )
    assert response and response.status_code == 200, "unexpected response"


def test_url_creds(client: TestClient, db: Database, test_data: TestData):
    """
    Test to check if login endpoint accepts usermane and password in url instead of data
    """
    response = client.post(
        f"api/auth/login?username={test_data.test_users[0].name}&password={test_data.test_users[0].password}",
    )
    assert response.status_code == 422


def test_signup(client: TestClient, db: Database, test_data: TestData):
    response = client.post("api/auth/sign-up", json=test_data.test_user.dict())
    assert response and response.status_code == 201
    assert db.users.find_one({"email": test_data.test_user.email})


def test_get_all_users(client_a: TestClient, db: Database, test_data: TestData):
    response = client_a.get("api/user/all")
    assert response and response.status_code == 200
    user_list = s.UserList.parse_obj(response.json())
    assert user_list
    assert len(user_list.users) == len(test_data.test_users) + 1


def test_get_user_by_id(client_a: TestClient, db: Database, test_data: TestData):
    test_user: s.UserDB = s.UserDB.parse_obj(db.users.find_one())

    response = client_a.get(f"api/user/{test_user.id}")
    assert response and response.status_code == 200
    res_user = s.UserDB.parse_obj(response.json())
    assert res_user.name == test_user.name


def test_update_user(client_a: TestClient, db: Database, test_data: TestData):
    test_user: s.UserDB = s.UserDB.parse_obj(db.users.find_one())
    email_before = test_user.email
    username_before = test_user.name
    response = client_a.put(
        f"api/user/{test_user.id}",
        json=s.UserUpdate(
            name="New Username",
            email="new_email@gmail.com",
        ).dict(exclude_none=True),
    )
    assert response and response.status_code == 200
    user = s.UserDB.parse_obj(response.json())
    assert user.v == 1
    assert user != test_user

    response = client_a.put(
        f"api/user/{test_user.id}",
        json=s.UserUpdate(
            name=username_before,
            email=email_before,
        ).dict(),
    )
    assert response and response.status_code == 200
    user = s.UserDB.parse_obj(response.json())
    assert user.v == 2
    assert user.name == test_user.name


def test_delete_user(client_a: TestClient, db: Database, test_data: TestData):
    test_user: s.UserDB = s.UserDB.parse_obj(db.users.find_one())
    users_number_before = db.users.count_documents({})

    response = client_a.delete(f"api/user/{test_user.id}")
    assert response and response.status_code == 200

    users_number_after = db.users.count_documents({})
    assert users_number_before > users_number_after


def test_refresh(client: TestClient, db: Database, test_data: TestData):
    response = client.post(
        "api/auth/login",
        data=s.UserLogin(
            username=test_data.test_users[0].name,
            password=test_data.test_users[0].password,
        ).dict(),
    )
    assert response
    response_data = s.Tokens.parse_obj(response.json())
    refresh_token: str = response_data.refresh_token
    response = client.post(
        "api/auth/refresh",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json().get("access_token"), str)
    assert len(response.json().get("access_token")) == 155

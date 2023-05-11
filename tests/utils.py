from pymongo.database import Database
from app import schema as s, get_settings, make_hash
from tests.fixture import TestData


def create_test_superuser(db: Database, test_data):
    cfg = get_settings()
    user = s.UserDB(
        username=cfg.ADMIN_USER,
        email=test_data.test_superuser.email,
        password_hash=make_hash(test_data.test_superuser.password),
    )
    db.users.insert_one(user.dict())


def fill_db_by_test_data(db: Database, test_data: TestData):
    print("Filling up db with fake data")
    create_test_superuser(db, test_data)
    for u in test_data.test_users:
        user = s.UserDB(
            username=u.username,
            email=u.email,
            password_hash=make_hash(u.password),
        )
        db.users.insert_one(user.dict())

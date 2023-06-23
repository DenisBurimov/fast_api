import json
from pymongo.database import Database
from app import schema as s, make_hash
from tests.fixture import TestData


def create_test_superuser(db: Database, test_data):
    user: s.UserCreate = test_data.test_superuser
    user.password_hash = make_hash(user.password)
    db.users.insert_one(user.dict(exclude={"password": True}))


def fill_db_by_test_data(db: Database, test_data: TestData):
    print("Filling up db with fake data")
    create_test_superuser(db, test_data)
    for u in test_data.test_users:
        u.password_hash = make_hash(u.password)
        db.users.insert_one(u.dict(exclude={"password": True}))

    with open("tests/test_sleep.json") as sleep_file:
        sleep_data = json.load(sleep_file)

        for sleep_item in sleep_data:
            db.sleep_items.insert_one(sleep_item)

    with open("tests/test_logbook.json") as f:
        logbook_data = json.load(f)
        for data_item in logbook_data:
            logbook_item = s.JournalBase.parse_obj(data_item)
            db.journal_items.insert_one(logbook_item.dict())

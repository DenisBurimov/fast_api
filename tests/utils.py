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

    with open("tests/test_sleep_items.json") as sleep_file:
        sleep_data = json.load(sleep_file)

        TEST_USER = db.users.find_one({"email": test_data.test_users[0].email})
        for sleep_item in sleep_data:
            sleep_item["user_id"] = str(TEST_USER["_id"])
            db.sleep_items.insert_one(sleep_item)

    with open("tests/test_burn_items.json") as burn_file:
        burn_data = json.load(burn_file)

        TEST_USER = db.users.find_one({"email": test_data.test_users[0].email})
        for burn_item in burn_data:
            burn_item["user_id"] = str(TEST_USER["_id"])
            db.burn_items.insert_one(s.BurnResult.parse_obj(burn_item).dict())

    with open("tests/test_logbook.json") as f:
        logbook_data = json.load(f)
        for data_item in logbook_data:
            logbook_item = s.JournalBase.parse_obj(data_item)
            db.journal_items.insert_one(logbook_item.dict())

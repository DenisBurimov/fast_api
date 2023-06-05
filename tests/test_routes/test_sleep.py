from fastapi.testclient import TestClient
from pymongo.database import Database
import app.schema as s
from tests.fixture import TestData


TEST_SLEEP_ITEM = {
    "_id": {"$oid": "640a17f89d770e182aced59a"},
    "sleep_duration": {"numberInt": "389"},
    "sleep_intervals": [
        {"start": "22:37:00", "end": "8:45:00", "level": 0},
        {"start": "8:45:00", "end": "10:15:00", "level": 1},
        {"start": "10:15:00", "end": "11:50:00", "level": 2},
        {"start": "11:50:00", "end": "12:20:00", "level": 1},
        {"start": "12:20:00", "end": "13:15:00", "level": 2},
        {"start": "13:15:00", "end": "13:45:00", "level": 1},
        {"start": "13:45:00", "end": "15:20:00", "level": 2},
        {"start": "15:20:00", "end": "15:50:00", "level": 1},
        {"start": "15:50:00", "end": "17:25:00", "level": 2},
        {"start": "17:25:00", "end": "17:55:00", "level": 1},
        {"start": "17:55:00", "end": "19:30:00", "level": 2},
        {"start": "19:30:00", "end": "20:00:00", "level": 1},
        {"start": "20:00:00", "end": "24:00:00", "level": 0},
    ],
    "createdAt": {"$date": {"$numberLong": "1678383096251"}},
    "__v": {"$numberInt": "0"},
}


def test_create_sleep_item(client_a: TestClient, db: Database, test_data: TestData):
    response = client_a.post(
        "api/sleep/add",
        data=test_data.test_sleep_items[0].json(by_alias=True),
    )
    assert response.status_code == 201


def test_get_all_sleep_items(client_a: TestClient, db: Database, test_data: TestData):
    response = client_a.get("api/sleep/all")
    assert response.status_code == 200
    sleep_items_list = s.SleepList.parse_obj(response.json())
    assert sleep_items_list
    assert len(sleep_items_list.sleep_items) == len(test_data.test_sleep_items)


def test_get_sleep_item_by_id(client_a: TestClient, db: Database, test_data: TestData):
    item_to_get_id = db.sleep_items.find_one().get("_id")
    response = client_a.get(f"api/sleep/{str(item_to_get_id)}")
    assert response.status_code == 200
    assert s.SleepDB.parse_obj(response.json()).id == item_to_get_id


def test_delete_sleep_item(client_a: TestClient, db: Database, test_data: TestData):
    test_sleep_item: s.SleepDB = s.SleepDB.parse_obj(db.sleep_items.find_one())
    sleep_items_number_before = db.sleep_items.count_documents({})

    response = client_a.delete(f"api/sleep/{test_sleep_item.id}")
    assert response and response.status_code == 200

    sleep_items_number_after = db.sleep_items.count_documents({})
    assert sleep_items_number_before > sleep_items_number_after

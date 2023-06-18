import json
from fastapi.testclient import TestClient
from pymongo.database import Database
import app.schema as s
from tests.fixture import TestData


def test_create_sleep_item(client_a: TestClient, db: Database, test_data: TestData):
    with open("tests/test_sleep.json") as f:
        data = json.load(f)
    response = client_a.post(
        "api/sleep/add",
        # json=test_data.test_sleep_items[0].dict(),
        json=data,
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

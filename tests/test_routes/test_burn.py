from datetime import datetime
import json
import pytz
from fastapi.testclient import TestClient
from pymongo.database import Database
import app.schema as s
from tests.fixture import TestData


def test_create_burn_item(client_a: TestClient, db: Database, monkeypatch):
    burn_items_number_before = db.burn_items.count_documents({})

    def mock_ml_response(data):
        return s.BurnResult(
            statusCode=200,
            headers={"Content-Type": "application/json"},
            body='{"eye_droop": 0.1, "gaze_error": 0.8, "reaction_time": 513, "burn_rating": 98}',
        )

    monkeypatch.setattr("app.router.burn.ml_response", mock_ml_response)

    # with open("tests/burn_example.json") as f:
    with open("tests/test_burn.json") as f:
        data = json.load(f)
    response = client_a.post(
        "api/burn/add",
        # json=test_data.test_burn_items[0].dict(),
        json=data,
    )
    burn_items_number_after = db.burn_items.count_documents({})
    assert response.status_code == 201
    assert burn_items_number_after == burn_items_number_before + 1


def test_get_all_burn_items(client_a: TestClient, db: Database, test_data: TestData):
    db.burn_items.insert_many(
        [
            {"burn_values": [33, 0, 333, 0], "created_at": "2023-05-05T05:05:05+01:00"},
            {"burn_values": [55, 0, 555, 0], "created_at": "2023-07-14T07:07:07+07:00"},
            {"burn_values": [77, 0, 777, 0], "created_at": "2023-12-23T12:12:12+05:00"},
        ]
    )
    response = client_a.get("api/burn/all")
    assert response.status_code == 200
    burn_items_list = s.BurnList.parse_obj(response.json())
    assert burn_items_list
    assert len(burn_items_list.burn_items) == 3


def test_get_burn_item_by_id(client_a: TestClient, db: Database, test_data: TestData):
    db.burn_items.insert_many(
        [
            {"burn_values": [33, 0, 333, 0], "created_at": "2023-05-05T05:05:05+01:00"},
            {"burn_values": [55, 0, 555, 0], "created_at": "2023-07-14T07:07:07+07:00"},
            {"burn_values": [77, 0, 777, 0], "created_at": "2023-12-23T12:12:12+05:00"},
        ]
    )
    item_to_get_id = db.burn_items.find_one().get("_id")
    response = client_a.get(f"api/burn/id/{str(item_to_get_id)}")
    assert response.status_code == 200
    assert (
        list(db.burn_items.find({"_id": item_to_get_id}))[0].get("_id")
        == item_to_get_id
    )


def test_get_burn_item_by_time(client_a: TestClient, db: Database, test_data: TestData):
    tz = pytz.timezone("Europe/Kyiv")
    just_now = datetime.now(tz).isoformat()
    db.burn_items.insert_many(
        [
            {"burn_values": [33, 0, 333, 0], "created_at": "2023-05-05T05:05:05+01:00"},
            {"burn_values": [55, 0, 555, 0], "created_at": "2023-07-14T07:07:07+07:00"},
            {"burn_values": [77, 0, 777, 0], "created_at": "2023-12-23T12:12:12+05:00"},
            {"burn_values": [77, 0, 777, 0], "created_at": "2023-12-23T12:12:12+05:00"},
            {"burn_values": [33, 0, 333, 0], "created_at": just_now},
        ]
    )

    response = client_a.get(f"api/burn/time/{just_now}")
    assert response.status_code == 200
    assert s.BurnResultDB.parse_obj(response.json()).created_at == just_now


def test_get_burn_item_by_date(client_a: TestClient, db: Database, test_data: TestData):
    tz = pytz.timezone("Europe/Kyiv")
    today = datetime.today().isoformat()
    db.burn_items.insert_many(
        [
            {"burn_values": [33, 0, 333, 0], "created_at": "2023-05-05T05:05:05+01:00"},
            {"burn_values": [55, 0, 555, 0], "created_at": "2023-07-14T07:07:07+07:00"},
            {"burn_values": [77, 0, 777, 0], "created_at": "2023-12-23T12:12:12+05:00"},
            {"burn_values": [77, 0, 777, 0], "created_at": "2023-12-23T12:12:12+05:00"},
            {
                "burn_values": [11, 0, 111, 0],
                "created_at": datetime.now(tz).isoformat(),
            },
            {
                "burn_values": [22, 0, 222, 0],
                "created_at": datetime.now(tz).isoformat(),
            },
            {
                "burn_values": [34, 0, 43, 0],
                "created_at": datetime.now(tz).isoformat(),
            },
        ]
    )

    response = client_a.get(f"api/burn/date/{today}")
    assert response.status_code == 200
    assert len(s.BurnList.parse_obj(response.json()).burn_items) == 3

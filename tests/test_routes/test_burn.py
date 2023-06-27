from datetime import datetime
import json
from fastapi.testclient import TestClient
from pymongo.database import Database
import app.schema as s
from tests.fixture import TestData

"""
The burn json input version 2023-06-15
-----

{"_id":{"$oid":"640a17f89d770e182aced59a"},
"burnResponse": {
"burn": x,
"reaction_time": y,
"gaze_uniformity": z,
"peak_velocity": w,
"range": str,
"time": datetime ISO format
},
// enum suite for range ['low', 'moderate', 'high', 'burnout']
"logbookResponse": [
{"activity": "meditation", "value": 20, "timing": 1},
{"activity": "ice_bath", "value": 20, "timing": 0},
{"activity": "supplements", "value": 200, "timing": 2},
{"activity": "cold_shower", "timing": 2}
]
}
"""

TEST_BURN_ITEMS = [
    s.BurnResult(
        burnResponse={
            "burn": 0.1,
            "reaction_time": 0.2,
            "gaze_uniformity": 0.3,
            "peak_velocity": 0.4,
            "range": "moderate",
            "time": "2023-06-12T03:58:40+00:00",
        },
        logBookResponse=[],
    ),
    s.BurnResult(
        burnResponse={
            "burn": 0.21,
            "reaction_time": 0.22,
            "gaze_uniformity": 0.23,
            "peak_velocity": 0.24,
            "range": "high",
            "time": "2023-07-14T07:07:40+07:00",
        },
        logBookResponse=[
            {"activity": "meditation", "value": 30, "timing": 1},
            {"activity": "ice_bath", "value": 30, "timing": 0},
            {"activity": "supplements", "value": 400, "timing": 2},
            {"activity": "cold_shower", "value": 20, "timing": 2},
        ],
    ),
    s.BurnResult(
        burnResponse={
            "burn": 0.31,
            "reaction_time": 0.32,
            "gaze_uniformity": 0.33,
            "peak_velocity": 0.34,
            "range": "high",
            "time": "2023-05-05T05:05:05+01:00",
        },
        logBookResponse=[
            {"activity": "meditation", "value": 50, "timing": 1},
            {"activity": "ice_bath", "value": 50, "timing": 0},
            {"activity": "supplements", "value": 500, "timing": 2},
            {"activity": "cold_shower", "value": 50, "timing": 2},
        ],
        created_at="2023-05-05T05:05:05+01:00",
    ),
    s.BurnResult(
        burnResponse={
            "burn": 0.31,
            "reaction_time": 0.32,
            "gaze_uniformity": 0.33,
            "peak_velocity": 0.34,
            "range": "high",
            "time": "2023-07-14T07:07:07+07:00",
        },
        logBookResponse=[
            {"activity": "meditation", "value": 50, "timing": 1},
            {"activity": "ice_bath", "value": 50, "timing": 0},
            {"activity": "supplements", "value": 500, "timing": 2},
            {"activity": "cold_shower", "value": 50, "timing": 2},
        ],
        created_at="2023-07-14T07:07:07+07:00",
    ),
    s.BurnResult(
        burnResponse={
            "burn": 0.31,
            "reaction_time": 0.32,
            "gaze_uniformity": 0.33,
            "peak_velocity": 0.34,
            "range": "high",
            "time": "2023-12-23T12:12:12+05:00",
        },
        logBookResponse=[
            {"activity": "meditation", "value": 50, "timing": 1},
            {"activity": "ice_bath", "value": 50, "timing": 0},
            {"activity": "supplements", "value": 500, "timing": 2},
            {"activity": "cold_shower", "value": 50, "timing": 2},
        ],
        created_at="2023-12-23T12:12:12+05:00",
    ),
]

with open("tests/test_burn_items.json") as output_file:
    output_data = json.load(output_file)


def test_create_burn_item_with_logbook(client_a: TestClient, db: Database, monkeypatch):
    burn_items_number_before = db.burn_items.count_documents({})

    def mock_ml_response(data):
        return TEST_BURN_ITEMS[0]

    monkeypatch.setattr("app.router.burn.ml_response", mock_ml_response)

    with open("tests/test_burn.json") as f:
        data = json.load(f)
    response = client_a.post(
        "api/burn/add",
        json=data,
    )
    burn_items_number_after = db.burn_items.count_documents({})
    assert response.status_code == 201
    assert burn_items_number_after == burn_items_number_before + 1


def test_get_all_burn_items(client_a: TestClient, db: Database, test_data: TestData):
    response = client_a.get("api/burn/all")
    assert response.status_code == 200
    burn_items_list = s.BurnList.parse_obj(response.json())
    assert burn_items_list
    assert len(burn_items_list.burn_items) == len(output_data)


def test_get_burn_item_by_id(client_a: TestClient, db: Database, test_data: TestData):
    item_to_get_id = db.burn_items.find_one().get("_id")
    response = client_a.get(f"api/burn/id/{str(item_to_get_id)}")
    assert response.status_code == 200
    assert (
        list(db.burn_items.find({"_id": item_to_get_id}))[0].get("_id")
        == item_to_get_id
    )


def test_get_burn_item_by_time(client_a: TestClient, db: Database, test_data: TestData):
    exact_time = db.burn_items.find_one().get("created_at")
    response = client_a.get(f"api/burn/time/{exact_time}")
    assert response.status_code == 200
    assert s.BurnResultDB.parse_obj(response.json()).created_at == exact_time


def test_get_burn_item_by_date(client_a: TestClient, db: Database, test_data: TestData):
    today = datetime.today().isoformat()
    response = client_a.get(f"api/burn/date/{today}")
    assert response.status_code == 200
    assert len(s.BurnList.parse_obj(response.json()).burn_items) == len(output_data)


def test_get_X_burn_items(client_a: TestClient, db: Database, test_data: TestData):
    TEST_ITEMS_NUMBER = 3
    db.burn_items.insert_many(x.dict() for x in TEST_BURN_ITEMS)

    response = client_a.get(f"api/burn/last/{TEST_ITEMS_NUMBER}")
    assert response.status_code == 200
    assert len(s.BurnList.parse_obj(response.json()).burn_items) == TEST_ITEMS_NUMBER


def test_update_burn_item(client_a: TestClient, db: Database, test_data: TestData):
    item_to_update = db.burn_items.find_one().get("_id")
    logBookResponse = [
        {"activity": "meditation", "value": 50, "timing": 5},
        {"activity": "ice_bath", "value": 50, "timing": 5},
        {"activity": "supplements", "value": 500, "timing": 5},
        {"activity": "cold_shower", "value": 50, "timing": 5},
    ]
    response = client_a.put(
        f"api/burn/update/{str(item_to_update)}",
        json=s.BurnUpdate(logBookResponse=logBookResponse).dict(),
    )
    assert response.status_code == 200
    assert s.BurnResultDB.parse_obj(response.json()).logBookResponse == logBookResponse
    assert s.BurnResultDB.parse_obj(response.json()).v == 1

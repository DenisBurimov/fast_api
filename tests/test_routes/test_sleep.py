import json
from fastapi.testclient import TestClient
from pymongo.database import Database
import app.schema as s


"""
{"_id":{"$oid":"640a17f89d770e182aced59a"},
"sleepLastNight": int, // sleep duration
"sleepTimeline": [{"start": str, "end": str},
                    {"start": str, "end": str},
                    {"start": str, "end": str},
                    {"start": str, "end": str}]
"focusTimeline": [{"start": str, "end": str, "level": 0},
                    {"start": str, "end": str, "level": 1},
                    {"start": str, "end": str, "level": 2},
                    {"start": str, "end": str, "level": 1},
                    {"start": str, "end": str, "level": 2},
                    {"start": str, "end": str, "level": 1},
                    {"start": str, "end": str, "level": 2}]
"createdAt":{"$date":{"$numberLong":"1678383096251"}},
"__v":{"$numberInt":"0"}}
"""

with open("tests/test_sleep.json") as f:
    data = json.load(f)


def test_create_sleep_item(client_a: TestClient, db: Database, monkeypatch):
    def mock_ml_response(data):
        return s.SleepResult(
            sleepLastNight=6,
            sleepTimeline=[
                {
                    "start": "2023-06-14T01:01:01+01:00",
                    "end": "2023-06-14T07:07:07+01:00",
                },
                {
                    "start": "2023-06-15T01:01:01+01:00",
                    "end": "2023-06-15T07:07:07+01:00",
                },
                {
                    "start": "2023-06-16T01:01:01+01:00",
                    "end": "2023-06-16T07:07:07+01:00",
                },
            ],
            focusTimeline=[
                {
                    "start": "2023-06-11T01:01:01+01:00",
                    "end": "2023-06-11T01:01:01+01:00",
                    "level": 0,
                },
                {
                    "start": "2023-06-12T01:01:01+01:00",
                    "end": "2023-06-12T01:01:01+01:00",
                    "level": 0,
                },
                {
                    "start": "2023-06-13T01:01:01+01:00",
                    "end": "2023-06-13T01:01:01+01:00",
                    "level": 0,
                },
                {
                    "start": "2023-06-17T01:01:01+01:00",
                    "end": "2023-06-17T01:01:01+01:00",
                    "level": 0,
                },
                {
                    "start": "2023-06-18T01:01:01+01:00",
                    "end": "2023-06-18T01:01:01+01:00",
                    "level": 0,
                },
            ],
        )

    monkeypatch.setattr("app.router.sleep.ml_response", mock_ml_response)
    response = client_a.post(
        "api/sleep/add",
        json=data[0],
    )
    assert response.status_code == 201


def test_get_all_sleep_items(client_a: TestClient, db: Database):
    response = client_a.get("api/sleep/all")
    assert response.status_code == 200
    sleep_items_list = s.SleepList.parse_obj(response.json())
    assert sleep_items_list
    assert len(sleep_items_list.sleep_items) == len(data)


def test_get_sleep_item_by_id(client_a: TestClient, db: Database):
    item_to_get_id = db.sleep_items.find_one().get("_id")
    response = client_a.get(f"api/sleep/{str(item_to_get_id)}")
    assert response.status_code == 200
    assert s.SleepDB.parse_obj(response.json()).id == item_to_get_id

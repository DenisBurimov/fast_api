from fastapi.testclient import TestClient
from pymongo.database import Database
import app.schema as s
from tests.fixture import TestData


SLEEP_TEST_DATA = [
    {
        "data": {
            "date": "2023-01-31 03:00:00+00:00",
            "message": "Diagnostics message",
            "data": {},
        },
        "type": "diagnostics",
    },
    {
        "data": {
            "value": 0,
            "startDate": "2023-01-31 03:00:00+00:00",
            "endDate": "2023-01-31 13:00:00+00:00",
            "source": "Apple Watch",
        },
        "type": "sleep",
    },
    {
        "data": {
            "date": "2023-01-31 03:00:00+00:00",
            "x": -0.019287109375,
            "y": -0.0205078125,
            "z": -0.996826171875,
        },
        "type": "accelerometer",
    },
    {
        "data": {
            "date": "2023-01-31 03:00:00+00:00",
            "unknown": 0,
            "stationary": 0,
            "walking": 1,
            "running": 0,
            "automotive": 0,
            "cycling": 0,
        },
        "type": "step",
    },
    {
        "data": {
            "startDate": "2023-01-31 03:00:00+00:00",
            "endDate": "2023-01-31 04:00:00+00:00",
            "numberOfSteps": 6500,
            "distance": 10.5,
            "floorsAscended": 20,
            "floorsDescended": 20,
            "currentPace": 0.5,
            "currentCadence": 1.5,
            "averageActivePace": 0.8,
        },
        "type": "pedometer",
    },
]


def test_create_sleep_item(client_a: TestClient, db: Database, test_data: TestData):
    response = client_a.post(
        "api/sleep/add",
        json=s.SleepCreate(sleep_data=SLEEP_TEST_DATA).dict(),
    )
    assert response.status_code == 201


def test_get_all_users(client_a: TestClient, db: Database, test_data: TestData):
    TEST_ITEMS_NUMBER = 3
    for i in range(TEST_ITEMS_NUMBER):
        db.sleep_items.insert_one(s.SleepCreate(sleep_data=SLEEP_TEST_DATA).dict())
    response = client_a.get("api/sleep/all")
    assert response.status_code == 200
    sleep_items_list = s.SleepList.parse_obj(response.json())
    assert sleep_items_list
    assert len(sleep_items_list.sleep_items) == TEST_ITEMS_NUMBER

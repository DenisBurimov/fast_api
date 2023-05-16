from fastapi.testclient import TestClient
from pymongo.database import Database
import app.schema as s
from tests.fixture import TestData


TEST_BURN_ITEM = {
    "sessionInfo": "0B872D59-1E80-4A7F-9743-41A7D56DA73C",
    "timeStamps": {
        "beginTimeZone": "Friday, 27 January 2023 at 10:22:06 Central European Standard Time",
        "beginTime": 0,
        "endTime": 30.353888988494873,
    },
    "deviceInfo": {
        "deviceName": "iPhone",
        "iosVersion": "16.2",
        "UUID": "4BAACF6E-91FC-4A93-A383-C9398E80F42C",
    },
    "leftPupilInfo": [
        {
            "droopInfo": 0.06788557767868042,
            "timePoint": 0.062120914459228516,
            "pupilX": 0.012180243618786335,
            "pupilY": -0.07051916420459747,
        },
        {
            "droopInfo": 0.06792465597391129,
            "timePoint": 0.08002281188964844,
            "pupilX": 0.012866710312664509,
            "pupilY": -0.07073412090539932,
        },
    ],
    "rightPupilInfo": [
        {
            "droopInfo": 0.06788531690835953,
            "timePoint": 0.06208181381225586,
            "pupilX": 0.08784681558609009,
            "pupilY": -0.06998830288648605,
        },
        {
            "droopInfo": 0.06792449951171875,
            "timePoint": 0.08002185821533203,
            "pupilX": 0.08852659165859222,
            "pupilY": -0.0701945573091507,
        },
    ],
    "leftBlinkInfo": {
        "blinkTotalDurations": [148, 112],
        "blinkReopeningDurations": [99, 67],
        "blinkStartTimes": [0.8153500556945801, 5.517504930496216],
        "blinkFreq": 2.351508776603492,
        "blinkEndTimes": [0.9644169807434082, 5.631086826324463],
        "blinkClosingDurations": [49, 45],
        "totalBlinks": 2,
    },
    "rightBlinkInfo": {
        "blinkTotalDurations": [148, 112],
        "blinkReopeningDurations": [99, 67],
        "blinkStartTimes": [0.8153479099273682, 5.517493724822998],
        "blinkFreq": 2.3515091501382703,
        "blinkEndTimes": [0.9643518924713135, 5.631079912185669],
        "blinkClosingDurations": [49, 45],
        "totalBlinks": 2,
    },
}


def test_create_burn_item(client_a: TestClient, db: Database, test_data: TestData):
    burn_items_number_before = db.burn_items.count_documents({})
    response = client_a.post(
        "api/burn/add",
        json=s.BurnBase(burn_data=TEST_BURN_ITEM).dict(),
    )
    burn_items_number_after = db.burn_items.count_documents({})
    assert response.status_code == 201
    assert burn_items_number_after == burn_items_number_before + 1


def test_get_all_burn_items(client_a: TestClient, db: Database, test_data: TestData):
    response = client_a.get("api/burn/all")
    assert response.status_code == 200
    burn_items_list = s.BurnList.parse_obj(response.json())
    assert burn_items_list
    assert len(burn_items_list.burn_items) == len(test_data.test_burn_items)


def test_get_burn_item_by_id(client_a: TestClient, db: Database, test_data: TestData):
    item_to_get_id = db.burn_items.find_one().get("_id")
    response = client_a.get(f"api/burn/{str(item_to_get_id)}")
    assert response.status_code == 200
    assert s.BurnDB.parse_obj(response.json()).id == item_to_get_id

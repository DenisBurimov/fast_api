from fastapi.testclient import TestClient
from pymongo.database import Database
import app.schema as s

# from tests.fixture import TestData


TEST_RAW_BURN_ITEM = {
    "burn_values": "[x, y, z, w]",
    "createdAt": {"$date": {"$numberLong": "1678383096251"}},
}

TEST_CLEAN_BURN_ITEM = {
    "burn_values": "[x, y, z, w]",
    "createdAt": {"date": {"numberLong": "1678383096251"}},
}


def test_create_burn_item(client_a: TestClient, db: Database):
    burn_items_number_before = db.burn_items.count_documents({})
    response = client_a.post("api/burn/add", json=TEST_RAW_BURN_ITEM)
    burn_items_number_after = db.burn_items.count_documents({})
    assert response.status_code == 201
    assert burn_items_number_after == burn_items_number_before + 1


def test_get_all_burn_items(client_a: TestClient, db: Database):
    TEST_BURN_ITEMS_NUMBER = 5
    for _ in range(TEST_BURN_ITEMS_NUMBER):
        new_burn_item = s.BurnBase(
            burn_values=TEST_CLEAN_BURN_ITEM["burn_values"],
            created_at=TEST_CLEAN_BURN_ITEM["createdAt"],
        )
        db.burn_items.insert_one(new_burn_item.dict())
    response = client_a.get("api/burn/all")
    assert response.status_code == 200
    burn_items_list = s.BurnList.parse_obj(response.json())
    assert burn_items_list
    assert len(burn_items_list.burn_items) == len(list(db.burn_items.find()))


def test_get_burn_item_by_id(client_a: TestClient, db: Database):
    item_to_get_id = db.burn_items.find_one().get("_id")
    response = client_a.get(f"api/burn/{str(item_to_get_id)}")
    assert response.status_code == 200
    assert s.BurnDB.parse_obj(response.json()).id == item_to_get_id

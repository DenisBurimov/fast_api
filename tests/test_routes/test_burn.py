from fastapi.testclient import TestClient
from pymongo.database import Database
import app.schema as s
from tests.fixture import TestData


def test_create_burn_item(client_a: TestClient, db: Database, test_data: TestData):
    burn_items_number_before = db.burn_items.count_documents({})
    data = s.BurnBase.parse_obj(test_data.test_burn_items[0].dict())
    response = client_a.post("api/burn/add", data=data.json(by_alias=True))
    burn_items_number_after = db.burn_items.count_documents({})
    assert response.status_code == 201
    assert burn_items_number_after == burn_items_number_before + 1


def test_get_all_burn_items(client_a: TestClient, db: Database, test_data: TestData):
    response = client_a.get("api/burn/all")
    assert response.status_code == 200
    burn_items_list = s.BurnList.parse_obj(response.json())
    assert burn_items_list
    assert len(burn_items_list.burn_items) == len(test_data.test_burn_items)


def test_get_burn_item_by_id(client_a: TestClient, db: Database):
    item_to_get_id = db.burn_items.find_one().get("_id")
    response = client_a.get(f"api/burn/{str(item_to_get_id)}")
    assert response.status_code == 200
    assert s.BurnDB.parse_obj(response.json()).id == item_to_get_id

import json
from fastapi.testclient import TestClient
from pymongo.database import Database
import app.schema as s
from tests.fixture import TestData

with open("tests/test_logbook.json") as f:
    data = json.load(f)


def test_create_journal_item(client_a: TestClient, db: Database, test_data: TestData):
    response = client_a.post(
        "api/journal/add",
        json=data[0],
    )
    assert response.status_code == 201


def test_get_all_journal_items(client_a: TestClient, db: Database, test_data: TestData):
    response = client_a.get("api/journal/all")
    assert response.status_code == 200
    journal_items_list = s.JournalList.parse_obj(response.json())
    assert journal_items_list
    assert len(journal_items_list.journal_items) == len(data)


def test_get_journal_item_by_id(
    client_a: TestClient, db: Database, test_data: TestData
):
    item_to_get_id = db.journal_items.find_one().get("_id")
    response = client_a.get(f"api/journal/{str(item_to_get_id)}")
    assert response.status_code == 200
    assert s.JournalDB.parse_obj(response.json()).id == item_to_get_id

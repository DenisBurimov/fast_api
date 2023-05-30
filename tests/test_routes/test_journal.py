from fastapi.testclient import TestClient
from pymongo.database import Database
import app.schema as s
from tests.fixture import TestData


def test_create_journal_item(client_a: TestClient, db: Database, test_data: TestData):
    response = client_a.post(
        "api/journal/add",
        data=test_data.test_journal_items[0].json(by_alias=True),
    )
    assert response.status_code == 201


def test_get_all_journal_items(client_a: TestClient, db: Database, test_data: TestData):
    response = client_a.get("api/journal/all")
    assert response.status_code == 200
    journal_items_list = s.JournalList.parse_obj(response.json())
    assert journal_items_list
    assert len(journal_items_list.journal_items) == len(test_data.test_journal_items)


def test_get_journal_item_by_id(
    client_a: TestClient, db: Database, test_data: TestData
):
    item_to_get_id = db.journal_items.find_one().get("_id")
    response = client_a.get(f"api/journal/{str(item_to_get_id)}")
    assert response.status_code == 200
    assert s.JournalDB.parse_obj(response.json()).id == item_to_get_id


def test_delete_journal_item(client_a: TestClient, db: Database, test_data: TestData):
    test_journal_item: s.JournalDB = s.JournalDB.parse_obj(db.journal_items.find_one())
    journal_items_number_before = db.journal_items.count_documents({})

    response = client_a.delete(f"api/journal/{test_journal_item.id}")
    assert response and response.status_code == 200

    journal_items_number_after = db.journal_items.count_documents({})
    assert journal_items_number_before > journal_items_number_after

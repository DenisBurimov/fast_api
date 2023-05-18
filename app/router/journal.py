from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database
from pymongo import results
from bson.objectid import ObjectId
from app import get_db
import app.schema as s
from app.dependency import get_current_user
from app.logger import log

journal_router = APIRouter(prefix="/journal", tags=["JournalDB"])


@journal_router.post(
    "/add", status_code=status.HTTP_201_CREATED, response_model=s.JournalDB
)
def add_journal_item(
    data: s.JournalBase,
    db: Database = Depends(get_db),
    _: s.UserDB = Depends(get_current_user),
):
    res: results.InsertOneResult = db.journal_items.insert_one(data.dict())

    log(log.INFO, "Journal item [%s] has been saved", res.inserted_id)
    return s.JournalDB.parse_obj(db.journal_items.find_one({"_id": res.inserted_id}))


@journal_router.get("/all", response_model=s.JournalList)
def get_journal_items(
    db: Database = Depends(get_db),
    _: s.UserDB = Depends(get_current_user),
):
    return s.JournalList(
        journal_items=[s.JournalDB.parse_obj(o) for o in db.journal_items.find()]
    )


@journal_router.get("/{id}", response_model=s.JournalDB)
def get_journal_item_by_id(
    id: str,
    db: Database = Depends(get_db),
    _: s.UserDB = Depends(get_current_user),
):
    journal_item = db.journal_items.find_one({"_id": ObjectId(id)})
    if not journal_item:
        raise HTTPException(status_code=404, detail="This journal item was not found")

    return s.JournalDB.parse_obj(journal_item)


@journal_router.delete("/{id}", response_model=s.DeleteMessage)
def get_delete_user(
    id: str,
    db: Database = Depends(get_db),
    _: s.UserDB = Depends(get_current_user),
):
    res: results.DeleteResult = db.journal_items.delete_one({"_id": ObjectId(id)})
    if not res.deleted_count:
        raise HTTPException(status_code=404, detail="This user was not found")

    message = f"JournalDB {id} was successfully deleted"
    return s.DeleteMessage(message=message)

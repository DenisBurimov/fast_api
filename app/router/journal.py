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
    """
    Args:
        data (s.JournalBase): sleep item class instance.
        db (Database, optional): db generator.
        _ (s.UserDB, optional): Requires logged in user.

    Returns:
        schema.JournalBase class instance parsed by pydantic from the mongo object.
    """
    journal_item = db.journal_items.find_one({"_id": ObjectId(data.id)})
    if journal_item:
        log(log.ERROR, "Journal item [%s] already exists", data.id)
        raise HTTPException(status_code=409, detail="Journal item already exists")

    res: results.InsertOneResult = db.journal_items.insert_one(
        # We can't just pass data.dict() because mongo will give the new instance a new random id
        {
            "_id": ObjectId(data.id),
            "sleep_duration": data.sleep_duration,
            "activities": data.activities,
            "created_at": data.created_at,
        }
    )

    if res:
        log(log.INFO, "Journal item [%s] has been saved", res.inserted_id)
    log(log.INFO, "Something went wrong. Journal item has not been saved")
    return s.JournalDB.parse_obj(db.journal_items.find_one({"_id": res.inserted_id}))


@journal_router.get("/all", response_model=s.JournalList)
def get_journal_items(
    db: Database = Depends(get_db),
    _: s.UserDB = Depends(get_current_user),
):
    """
    Args:
        db (Database, optional): db generator.
        _ (s.UserDB, optional): Requires logged in user.

    Returns:
        schema.JournalList class instance with journal_items field, that contains all journal items
        It is a list of parsed with pydantic objects of journal_items collection from the db
    """
    journal_items = s.JournalList(
        journal_items=[s.JournalDB.parse_obj(o) for o in db.journal_items.find()]
    )
    if not journal_items:
        log(log.INFO, "Failed to get journal items")
    log(log.INFO, "Got [%d] journal items", len(journal_items.journal_items))
    return journal_items


@journal_router.get("/{id}", response_model=s.JournalDB)
def get_journal_item_by_id(
    id: str,
    db: Database = Depends(get_db),
    _: s.UserDB = Depends(get_current_user),
):
    """
    Args:
        id (str): String with users id (not an ObjectID!).
        db (Database, optional): db generator.
        _ (s.UserDB, optional): Requires logged in user.

    Raises:
        HTTPException: 404 if journal item with given id was not found.

    Returns:
        schema.JournalDB class instance parsed by pydantic from the mongo object.
    """
    journal_item = db.journal_items.find_one({"_id": ObjectId(id)})
    if not journal_item:
        log(log.INFO, "Failed to get journal item with id: %s", id)
        raise HTTPException(status_code=404, detail="This journal item was not found")

    log(log.INFO, "Journal item %s: %s", id, journal_item)
    return s.JournalDB.parse_obj(journal_item)


@journal_router.delete("/{id}", response_model=s.DeleteMessage)
def get_delete_journal_id(
    id: str,
    db: Database = Depends(get_db),
    _: s.UserDB = Depends(get_current_user),
):
    res: results.DeleteResult = db.journal_items.delete_one({"_id": ObjectId(id)})
    if not res.deleted_count:
        log(log.ERROR, "Journal item [%s] was not found", id)
        raise HTTPException(status_code=404, detail="This user was not found")

    log(log.INFO, "Journal item [%s] was successfully deleted", id)
    message = f"Journal item {id} was successfully deleted"
    return s.DeleteMessage(message=message)

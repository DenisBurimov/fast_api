from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database
from pymongo import results
from bson.objectid import ObjectId
from app import get_db
import app.schema as s

from app.dependency import get_current_user

sleep_item_router = APIRouter(prefix="/sleep", tags=["SleepItem"])


@sleep_item_router.get("/all", response_model=s.SleepList)
def get_sleep_items(
    db: Database = Depends(get_db),
    _: s.UserDB = Depends(get_current_user),
):
    return s.SleepList(sleep_items=[s.SleepDB.parse_obj(o) for o in db.sleeps.find()])


@sleep_item_router.get("/{id}", response_model=s.SleepDB)
def get_sleep_item_by_id(
    id: str,
    db: Database = Depends(get_db),
    _: s.UserDB = Depends(get_current_user),
):
    sleep_item = db.sleep_items.find_one({"_id": ObjectId(id)})
    if not sleep_item:
        raise HTTPException(status_code=404, detail="This sleep item was not found")

    return s.SleepDB.parse_obj(sleep_item)


@sleep_item_router.put("/{id}", response_model=s.SleepItem)
def get_update_sleep_item(
    id: str,
    data: s.SleepUpdate,
    db: Database = Depends(get_db),
    _: s.UserDB = Depends(get_current_user),
):
    db.sleep_items.update_one(
        {"_id": ObjectId(id)}, {"$set": data.dict(exclude_none=True)}
    )

    return s.SleepDB.parse_obj(db.sleep_items.find_one({"_id": ObjectId(id)}))


@sleep_item_router.delete("/{id}", response_model=s.DeleteMessage)
def get_delete_user(
    id: str,
    db: Database = Depends(get_db),
    _: s.UserDB = Depends(get_current_user),
):
    res: results.DeleteResult = db.sleep_items.delete_one({"_id": ObjectId(id)})
    if not res.deleted_count:
        raise HTTPException(status_code=404, detail="This user was not found")

    message = f"SleepItem {id} was successfully deleted"
    return s.DeleteMessage(message=message)

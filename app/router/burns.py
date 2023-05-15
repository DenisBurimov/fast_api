from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database
from pymongo import results
from bson.objectid import ObjectId
from app import get_db
import app.schema as s

from app.dependency import get_current_user

burn_item_router = APIRouter(prefix="/burn", tags=["BurnItem"])


@burn_item_router.get("/all", response_model=s.BurnItemsList)
def get_burn_items(
    db: Database = Depends(get_db),
    _: s.UserDB = Depends(get_current_user),
):
    return s.BurnItemsList(
        burn_items=[s.BurnItem.parse_obj(o) for o in db.burns.find()]
    )


@burn_item_router.get("/{id}", response_model=s.BurnItem)
def get_burn_item_by_id(
    id: str,
    db: Database = Depends(get_db),
    _: s.UserDB = Depends(get_current_user),
):
    burn_item = db.burn_items.find_one({"_id": ObjectId(id)})
    if not burn_item:
        raise HTTPException(status_code=404, detail="This burn item was not found")

    return s.BurnItem.parse_obj(burn_item)


@burn_item_router.put("/{id}", response_model=s.BurnItem)
def get_update_burn_item(
    id: str,
    data: s.BurnItemUpdate,
    db: Database = Depends(get_db),
    _: s.UserDB = Depends(get_current_user),
):
    db.burn_items.update_one(
        {"_id": ObjectId(id)}, {"$set": data.dict(exclude_none=True)}
    )

    return s.BurnItem.parse_obj(db.burn_items.find_one({"_id": ObjectId(id)}))


@burn_item_router.delete("/{id}", response_model=s.DeleteMessage)
def get_delete_user(
    id: str,
    db: Database = Depends(get_db),
    _: s.UserDB = Depends(get_current_user),
):
    res: results.DeleteResult = db.burn_items.delete_one({"_id": ObjectId(id)})
    if not res.deleted_count:
        raise HTTPException(status_code=404, detail="This user was not found")

    message = f"BurnItem {id} was successfully deleted"
    return s.DeleteMessage(message=message)

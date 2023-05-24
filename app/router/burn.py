from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database
from pymongo import results
from bson.objectid import ObjectId
from app import get_db
import app.schema as s
from app.dependency import get_current_user
from app.logger import log

burn_router = APIRouter(prefix="/burn", tags=["BurnDB"])


@burn_router.post("/add", status_code=status.HTTP_201_CREATED, response_model=s.BurnDB)
def add_burn_item(
    # data: s.BurnBase,
    data: dict,
    db: Database = Depends(get_db),
    _: s.UserDB = Depends(get_current_user),
):
    new_burn_item = {
        "burn_values": data["burn_values"],
        "created_at": {
            "date": {"numberLong": data["createdAt"]["$date"]["$numberLong"]}
        },
    }
    # res: results.InsertOneResult = db.burn_items.insert_one(data.dict())
    res: results.InsertOneResult = db.burn_items.insert_one(new_burn_item)

    log(log.INFO, "Burn item [%s] has been saved", res.inserted_id)
    return s.BurnDB.parse_obj(db.burn_items.find_one({"_id": res.inserted_id}))


@burn_router.get("/all", response_model=s.BurnList)
def get_burn_items(
    db: Database = Depends(get_db),
    _: s.UserDB = Depends(get_current_user),
):
    return s.BurnList(burn_items=[s.BurnDB.parse_obj(o) for o in db.burn_items.find()])


@burn_router.get("/{id}", response_model=s.BurnDB)
def get_burn_item_by_id(
    id: str,
    db: Database = Depends(get_db),
    _: s.UserDB = Depends(get_current_user),
):
    burn_item = db.burn_items.find_one({"_id": ObjectId(id)})
    if not burn_item:
        raise HTTPException(status_code=404, detail="This burn item was not found")

    return s.BurnDB.parse_obj(burn_item)


@burn_router.delete("/{id}", response_model=s.DeleteMessage)
def get_delete_user(
    id: str,
    db: Database = Depends(get_db),
    _: s.UserDB = Depends(get_current_user),
):
    res: results.DeleteResult = db.burn_items.delete_one({"_id": ObjectId(id)})
    if not res.deleted_count:
        raise HTTPException(status_code=404, detail="This user was not found")

    message = f"BurnDB {id} was successfully deleted"
    return s.DeleteMessage(message=message)

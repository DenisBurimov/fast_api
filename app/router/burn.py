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
    data: s.BurnBase,
    db: Database = Depends(get_db),
    _: s.UserDB = Depends(get_current_user),
):
    """
    Args:
        data (s.BurnBase): burn item class instance
        db: db generator.
        _ : Depends(get_current_user) - auth required.

    Raises:
        HTTPException: 409 Conflict if burn item with given id already exists

    Returns:
        schema.BurnDB class instance parsed by pydantic from the mongo object.
    """
    burn_item = db.burn_items.find_one({"_id": ObjectId(data.id)})
    if burn_item:
        log(log.ERROR, "Burn item [%s] already exists", data.id)
        raise HTTPException(status_code=409, detail="Burn item already exists")

    res: results.InsertOneResult = db.burn_items.insert_one(
        # We can't just pass data.dict() because mongo will give the new instance a new random id
        {
            "_id": ObjectId(data.id),  # Here we specify the exact id
            "burn_values": data.burn_values,
            "created_at": data.created_at,
            "v": data.v,
        }
    )

    log(log.INFO, "Burn item [%s] has been saved", res.inserted_id)
    return s.BurnDB.parse_obj(db.burn_items.find_one({"_id": res.inserted_id}))


@burn_router.get("/all", response_model=s.BurnList)
def get_burn_items(
    db: Database = Depends(get_db),
    _: s.UserDB = Depends(get_current_user),
):
    """
    Args:
        db: db generator.
        _ : Depends(get_current_user) - auth required.

    Returns:
        schema.BurnList class instance with burn_items field, that contains all burn items
        It is a list of parsed with pydantic objects of burn_items collection from the db
    """
    burn_items = s.BurnList(
        burn_items=[s.BurnDB.parse_obj(o) for o in db.burn_items.find()]
    )
    log(log.INFO, "[%d] burn items fetched", len(burn_items.burn_items))
    return burn_items


@burn_router.get("/{id}", response_model=s.BurnDB)
def get_burn_item_by_id(
    id: str,
    db: Database = Depends(get_db),
    _: s.UserDB = Depends(get_current_user),
):
    """
    Args:
        id (str): String with users id (not an ObjectID!).
        db (Database, optional): _description_. Defaults to Depends(get_db).
        _ (s.UserDB, optional): _description_. Defaults to Depends(get_current_user).

    Raises:
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
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

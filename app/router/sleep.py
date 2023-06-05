from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database
from pymongo import results
from bson.objectid import ObjectId
from app import get_db
import app.schema as s
from app.dependency import get_current_user
from app.logger import log

sleep_router = APIRouter(prefix="/sleep", tags=["SleepDB"])


@sleep_router.post(
    "/add", status_code=status.HTTP_201_CREATED, response_model=s.SleepDB
)
def add_sleep_item(
    data: s.SleepBase,
    db: Database = Depends(get_db),
    _: s.UserDB = Depends(get_current_user),
):
    """
    Args:
        data (s.SleepBase): sleep item class instance.
        db (Database, optional): db generator.
        _ (s.UserDB, optional): Requires logged in user.

    Returns:
        schema.SleepDB class instance parsed by pydantic from the mongo object.
    """
    res: results.InsertOneResult = db.sleep_items.insert_one(
        # We can't just pass data.dict() because mongo will give the new instance a new random id
        {
            "_id": ObjectId(data.id),
            "sleep_duration": data.sleep_duration,
            "sleep_intervals": data.sleep_intervals,
            "created_at": data.created_at,
        }
    )

    log(log.INFO, "Sleep item [%s] has been saved", res.inserted_id)
    return s.SleepDB.parse_obj(db.sleep_items.find_one({"_id": res.inserted_id}))


@sleep_router.get("/all", response_model=s.SleepList)
def get_sleep_items(
    db: Database = Depends(get_db),
    _: s.UserDB = Depends(get_current_user),
):
    """
    Args:
        db (Database, optional): db generator.
        _ (s.UserDB, optional): Requires logged in user.

    Returns:
        schema.SleepList class instance with sleep_items field, that contains all sleep items
        It is a list of parsed with pydantic objects of sleep_items collection from the db
    """
    sleep_items = s.SleepList(
        sleep_items=[s.SleepDB.parse_obj(o) for o in db.sleep_items.find()]
    )
    log(log.INFO, "[%d] sleep items fetched", len(sleep_items.sleep_items))
    return sleep_items


@sleep_router.get("/{id}", response_model=s.SleepDB)
def get_sleep_item_by_id(
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
        HTTPException: 404 if sleep item with given id was not found.

    Returns:
        schema.SleepDB class instance parsed by pydantic from the mongo object.
    """
    sleep_item = db.sleep_items.find_one({"_id": ObjectId(id)})
    if not sleep_item:
        log(log.ERROR, "Sleep item [%s] was not found", id)
        raise HTTPException(status_code=404, detail="This sleep item was not found")

    log(log.INFO, "sleep item %s: ", sleep_item)
    return s.SleepDB.parse_obj(sleep_item)


@sleep_router.delete("/{id}", response_model=s.DeleteMessage)
def get_delete_user(
    id: str,
    db: Database = Depends(get_db),
    _: s.UserDB = Depends(get_current_user),
):
    res: results.DeleteResult = db.sleep_items.delete_one({"_id": ObjectId(id)})
    if not res.deleted_count:
        log(log.ERROR, "Slepp item [%s] was not found", id)
        raise HTTPException(status_code=404, detail="This user was not found")

    log(log.INFO, "Sleep item [%s] was successfully deleted", id)
    message = f"Sleep item {id} was successfully deleted"
    return s.DeleteMessage(message=message)

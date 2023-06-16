from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database
from pymongo import results
from bson.objectid import ObjectId
from app import get_db
import app.schema as s
from app.config import Settings, get_settings
from app.dependency import get_current_user
from app.logger import log

sleep_router = APIRouter(prefix="/sleep", tags=["SleepDB"])


settings: Settings = get_settings()


def ml_response(data):
    ML_URL = (
        settings.SLEEP_MODEL_URL
        if settings.ENV_MODE == "production"
        else settings.SLEEP_MODEL_URL_LOCAL
    )
    ml_response = requests.post(
        ML_URL,
        # json=data_json,
        json=data.dict(),
    )

    try:
        burn_result = s.BurnResult.parse_raw(ml_response.text)
    except Exception:
        log(log.ERROR, "ML connection error: %s", ml_response.text)
        raise HTTPException(status_code=400, detail="ML model bad request")

    return burn_result


@sleep_router.post(
    "/add", status_code=status.HTTP_201_CREATED, response_model=s.SleepDB
)
def add_sleep_item(
    data: s.SleepBase,
    db: Database = Depends(get_db),
    _: s.UserDB = Depends(get_current_user),
):
    res: results.InsertOneResult = db.sleep_items.insert_one(data.dict())

    log(log.INFO, "Sleep item [%s] has been saved", res.inserted_id)
    return s.SleepDB.parse_obj(db.sleep_items.find_one({"_id": res.inserted_id}))


@sleep_router.get("/all", response_model=s.SleepList)
def get_sleep_items(
    db: Database = Depends(get_db),
    _: s.UserDB = Depends(get_current_user),
):
    return s.SleepList(
        sleep_items=[s.SleepDB.parse_obj(o) for o in db.sleep_items.find()]
    )


@sleep_router.get("/{id}", response_model=s.SleepDB)
def get_sleep_item_by_id(
    id: str,
    db: Database = Depends(get_db),
    _: s.UserDB = Depends(get_current_user),
):
    sleep_item = db.sleep_items.find_one({"_id": ObjectId(id)})
    if not sleep_item:
        raise HTTPException(status_code=404, detail="This sleep item was not found")

    return s.SleepDB.parse_obj(sleep_item)


@sleep_router.delete("/{id}", response_model=s.DeleteMessage)
def get_delete_user(
    id: str,
    db: Database = Depends(get_db),
    _: s.UserDB = Depends(get_current_user),
):
    res: results.DeleteResult = db.sleep_items.delete_one({"_id": ObjectId(id)})
    if not res.deleted_count:
        raise HTTPException(status_code=404, detail="This user was not found")

    message = f"SleepDB {id} was successfully deleted"
    return s.DeleteMessage(message=message)

# import json
# from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
import requests
from pymongo.database import Database
from pymongo import results
from bson.objectid import ObjectId
from app import get_db
import app.schema as s
from app.dependency import get_current_user
from app.logger import log
from app.config import Settings, get_settings


burn_router = APIRouter(prefix="/burn", tags=["BurnDB"])

settings: Settings = get_settings()


def ml_response(data):
    ML_URL = (
        settings.BURN_MODEL_URL
        if settings.ENV_MODE == "production"
        else settings.BURN_MODEL_URL_LOCAL
    )
    ml_response = requests.post(
        ML_URL,
        json=data.dict(),
    )

    try:
        burn_result = s.BurnResult.parse_raw(ml_response.text)
    except Exception:
        log(log.ERROR, "ML connection error: %s", ml_response.text)
        raise HTTPException(status_code=400, detail="ML model bad request")

    return burn_result


@burn_router.post(
    "/add", status_code=status.HTTP_201_CREATED, response_model=s.BurnResult
)
def add_burn_item(
    data: s.BurnBase,
    db: Database = Depends(get_db),
    current_user: s.UserDB = Depends(get_current_user),
):
    """
    Rename incoming schema to BurnRaw
    BurnRaw is received from the mobile side and then has to be sent to ML

    Add to the schema BurnResult instance
    BurnResult is received as a responce from the ML and has to be saved to database

    We don't save BurnRaw items to the database
    """

    # Here we have to send data (s.BurnRaw) to the ML
    # data_json = dict(body=json.dumps(data.dict()))

    burn_result = ml_response(data)
    # res: results.InsertOneResult = db.burn_items.insert_one(burn_result.dict())
    res: results.InsertOneResult = db.burn_items.insert_one(
        {
            "user_id": str(current_user.id),
            "burnResponse": [x for x in burn_result.burnResponse],
            "logBookResponse": [x for x in burn_result.logBookResponse],
        }
    )
    log(log.INFO, "Burn item [%s] has been saved", res.inserted_id)
    return s.BurnResult.parse_obj(db.burn_items.find_one({"_id": res.inserted_id}))


@burn_router.get("/all", response_model=s.BurnList)
def get_burn_items(
    db: Database = Depends(get_db),
    current_user: s.UserDB = Depends(get_current_user),
):
    users_burn_items = [
        s.BurnResult.parse_obj(o)
        for o in list(db.burn_items.find({"user_id": str(current_user.id)}))
    ]
    if not users_burn_items:
        return s.BurnList(burn_items=[])

    log(log.INFO, "[%s] user's sleep items retrieved", len(users_burn_items))
    return s.BurnList(burn_items=users_burn_items)


@burn_router.get("/id/{id}", response_model=s.BurnResultDB)
def get_burn_item_by_id(
    id: str,
    db: Database = Depends(get_db),
    current_user: s.UserDB = Depends(get_current_user),
):
    burn_item = db.burn_items.find_one(
        {"_id": ObjectId(id), "user_id": str(current_user.id)}
    )
    if not burn_item:
        raise HTTPException(status_code=404, detail="This burn item was not found")

    return s.BurnResultDB.parse_obj(burn_item)


@burn_router.get("/time/{created}", response_model=s.BurnResultDB)
def get_burn_item_by_time(
    created: str,
    db: Database = Depends(get_db),
    current_user: s.UserDB = Depends(get_current_user),
):
    burn_item = db.burn_items.find_one(
        {"created_at": created, "user_id": str(current_user.id)}
    )
    if not burn_item:
        raise HTTPException(status_code=404, detail="This burn item was not found")

    return s.BurnResultDB.parse_obj(burn_item)


@burn_router.get("/date/{day}", response_model=s.BurnList)
def get_burn_item_by_date(
    day: str,
    db: Database = Depends(get_db),
    current_user: s.UserDB = Depends(get_current_user),
):
    day_str = day.split("T")[0]
    burns_by_day = list(
        db.burn_items.find(
            {
                "created_at": {"$regex": f".*{day_str}.*"},
                "user_id": str(current_user.id),
            }
        )
    )

    if not burns_by_day:
        return s.BurnList(burn_items=[o for o in burns_by_day])

    return s.BurnList(burn_items=[s.BurnResultDB.parse_obj(o) for o in burns_by_day])


@burn_router.get("/last/{items_number}", response_model=s.BurnList)
def get_burn_X_items(
    items_number: int,
    db: Database = Depends(get_db),
    current_user: s.UserDB = Depends(get_current_user),
):
    last_items = list(
        db.burn_items.find({"user_id": str(current_user.id)})
        .sort("created_at", -1)
        .limit(items_number)
    )

    if not last_items:
        return s.BurnList(burn_items=[o for o in last_items])

    return s.BurnList(burn_items=[s.BurnResultDB.parse_obj(o) for o in last_items])


@burn_router.put("/update/{id}", response_model=s.BurnResultDB)
def update_burn_item(
    id: str,
    data: s.BurnUpdate,
    db: Database = Depends(get_db),
    current_user: s.UserDB = Depends(get_current_user),
):
    burn_item = db.burn_items.find_one(
        {"_id": ObjectId(id), "user_id": str(current_user.id)}
    )
    if not burn_item:
        raise HTTPException(status_code=404, detail="This burn item was not found")

    data.v = 1 if not burn_item.get("v") else burn_item["v"] + 1
    db.burn_items.update_one(
        {"_id": ObjectId(id)},
        {"$set": data.dict(exclude_none=True)},
    )

    return s.BurnResultDB.parse_obj(db.burn_items.find_one({"_id": ObjectId(id)}))

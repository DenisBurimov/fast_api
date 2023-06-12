import json
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


@burn_router.post(
    "/add", status_code=status.HTTP_201_CREATED, response_model=s.BurnResultBody
)
def add_burn_item(
    data: s.BurnBase,
    db: Database = Depends(get_db),
    _: s.UserDB = Depends(get_current_user),
):
    """
    Rename incoming schema to BurnRaw
    BurnRaw is received from the mobile side and then has to be sent to ML

    Add to the schema BurnResult instance
    BurnResult is received as a responce from the ML and has to be saved to database

    We don't save BurnRaw items to the database
    """
    # Here we have to send data (s.BurnRaw) to the ML
    data = dict(body=json.dumps(data.dict()))
    ml_response = requests.post(
        "http://localhost:9000/2015-03-31/functions/function/invocations",
        # data=data.json(),
        # json=data.dict(),
        json=data,
    )

    #
    burn_result = s.BurnResult.parse_raw(ml_response.text)
    body = s.BurnResultBody.parse_raw(burn_result.body)

    burn_rating = 100 if body.burn_rating > 100 else body.burn_rating
    burn_values = s.BurnResultBody(
        burn_rating=burn_rating,
        gaze_error=body.gaze_error,
        reaction_time=body.reaction_time,
        eye_droop=body.eye_droop,
    )

    res: results.InsertOneResult = db.burn_items.insert_one(burn_values.dict())

    log(log.INFO, "Burn item [%s] has been saved", res.inserted_id)
    return s.BurnResultBody.parse_obj(db.burn_items.find_one({"_id": res.inserted_id}))


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

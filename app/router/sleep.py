import json
import boto3
from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database
from pymongo import results
from bson.objectid import ObjectId
from app import get_db
import app.schema as s
from app.config import Settings, get_settings
from app.dependency import get_current_user
from app.logger import log
from pydantic import ValidationError

sleep_router = APIRouter(prefix="/sleep", tags=["SleepDB"])


settings: Settings = get_settings()


def ml_response(data):
    # ML_URL = (
    #     settings.SLEEP_MODEL_URL
    #     if settings.ENV_MODE == "production"
    #     else settings.SLEEP_MODEL_URL_LOCAL
    # )
    # ml_response = requests.post(
    #     ML_URL,
    #     # json=data_json,
    #     json=data.dict(),
    # )

    AWS_REGION = "us-east-1"
    client = boto3.client(
        "lambda",
        region_name=AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_KEY,
    )

    data = data.dict()

    response = client.invoke(
        FunctionName="oculo-sleep",
        Payload=json.dumps(data),
    )
    # Read the response payload as bytes
    response_payload = response['Payload'].read()

    # Decode the response payload assuming it's in UTF-8 encoding
    decoded_payload = response_payload.decode('utf-8')

    log(log.DEBUG, "response payload: %s", decoded_payload)

    try:
        payload_data = json.loads(decoded_payload)["body"]
        sleep_result_data = {
            "sleepLastNight": payload_data["sleepLastNight"],
            "sleepTimeline": payload_data["sleepTimeline"],
            "focusTimeline": payload_data["focusTimeline"]
        }
        sleep_result = s.SleepResult(**sleep_result_data)
        log(log.INFO, "SleepResult object created successfully: %s", sleep_result)
    except ValidationError as e:
        log(log.ERROR, "Validation error: %s", e)
        raise HTTPException(status_code=400, detail="Invalid ML model response")
    except Exception as e:
        log(log.ERROR, "ML connection error: %s", e)
        raise HTTPException(status_code=400, detail="ML model bad request")

    return sleep_result


@sleep_router.post(
    "/add", status_code=status.HTTP_201_CREATED, response_model=s.SleepResult
)
def add_sleep_item(
    data: s.SleepBase,
    db: Database = Depends(get_db),
    current_user: s.UserDB = Depends(get_current_user),
):
    sleep_result = ml_response(data)
    # res: results.InsertOneResult = db.sleep_items.insert_one(sleep_result.dict())
    res: results.InsertOneResult = db.sleep_items.insert_one(
        {
            "user_id": str(current_user.id),
            "sleepLastNight": sleep_result.sleepLastNight,
            "sleepTimeline": [x.dict() for x in sleep_result.sleepTimeline],
            "focusTimeline": [x.dict() for x in sleep_result.focusTimeline],
        }
    )

    log(log.INFO, "Sleep item [%s] has been saved", res.inserted_id)
    return s.SleepResult.parse_obj(db.sleep_items.find_one({"_id": res.inserted_id}))


@sleep_router.get("/all", response_model=s.SleepList)
def get_sleep_items(
    db: Database = Depends(get_db),
    current_user: s.UserDB = Depends(get_current_user),
):
    users_sleep_items = [
        s.SleepResult.parse_obj(o)
        for o in db.sleep_items.find({"user_id": str(current_user.id)})
    ]
    log(log.INFO, "[%s] user's sleep items retrieved", len(users_sleep_items))
    return s.SleepList(sleep_items=users_sleep_items)


@sleep_router.get("/{id}", response_model=s.SleepResult)
def get_sleep_item_by_id(
    id: str,
    db: Database = Depends(get_db),
    current_user: s.UserDB = Depends(get_current_user),
):
    sleep_item = db.sleep_items.find_one(
        {"_id": ObjectId(id), "user_id": str(current_user.id)}
    )
    if not sleep_item:
        raise HTTPException(status_code=404, detail="This sleep item was not found")

    return s.SleepResult.parse_obj(sleep_item)


@sleep_router.get("/date/{day}", response_model=s.SleepList)
def get_sleep_item_by_date(
    day: str,
    db: Database = Depends(get_db),
    current_user: s.UserDB = Depends(get_current_user),
):
    day_str = day.split("T")[0]
    sleep_by_day = list(
        db.SleepDB.find(
            {
                "created_at": {"$regex": f".*{day_str}.*"},
                "user_id": str(current_user.id),
            }
        )
    )

    if not sleep_by_day:
        return s.SleepList(sleep_items=[o for o in sleep_by_day])

    return s.SleepList(sleep_items=[s.SleepResult.parse_obj(o) for o in sleep_by_day])


@sleep_router.delete("/{id}", response_model=s.DeleteMessage)
def get_delete_user(
    id: str,
    db: Database = Depends(get_db),
    current_user: s.UserDB = Depends(get_current_user),
):
    res: results.DeleteResult = db.sleep_items.delete_one(
        {
            "_id": ObjectId(id),
            "user_id": str(current_user.id),
        }
    )
    if not res.deleted_count:
        raise HTTPException(status_code=404, detail="This user was not found")

    message = f"SleepDB {id} was successfully deleted"
    return s.DeleteMessage(message=message)

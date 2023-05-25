from datetime import datetime
from pydantic import BaseModel, Field, validator
from bson.objectid import ObjectId
from .db_object import DbObject


SLEEP_ITEM = {
    "_id": {"$oid": "640a17f89d770e182aced59a"},
    "sleep_duration": {"$numberInt": "389"},
    "sleep_intervals": [
        {"start": "22:37:00", "end": "8:45:00", "level": 0},
        {"start": "8:45:00", "end": "10:15:00", "level": 1},
        {"start": "10:15:00", "end": "11:50:00", "level": 2},
        {"start": "11:50:00", "end": "12:20:00", "level": 1},
        {"start": "12:20:00", "end": "13:15:00", "level": 2},
        {"start": "13:15:00", "end": "13:45:00", "level": 1},
        {"start": "13:45:00", "end": "15:20:00", "level": 2},
        {"start": "15:20:00", "end": "15:50:00", "level": 1},
        {"start": "15:50:00", "end": "17:25:00", "level": 2},
        {"start": "17:25:00", "end": "17:55:00", "level": 1},
        {"start": "17:55:00", "end": "19:30:00", "level": 2},
        {"start": "19:30:00", "end": "20:00:00", "level": 1},
        {"start": "20:00:00", "end": "24:00:00", "level": 0},
    ],
    "createdAt": {"$date": {"$numberLong": "1678383096251"}},
    "__v": {"$numberInt": "0"},
}


class SleepBase(BaseModel):
    id: str | None = Field(alias="_id")
    sleep_duration: int
    sleep_intervals: list[dict]
    created_at: datetime = Field(alias="createdAt")

    @validator("id", pre=True)
    def id_from_dict(cls, value: dict):
        if not isinstance(value, dict):
            return value
        return value.get("$oid")

    @validator("sleep_duration", pre=True)
    def sleep_duration_from_dict(cls, value: dict):
        if not isinstance(value, dict):
            return value
        return value.get("$numberInt")

    @validator("created_at", pre=True)
    def created_at_from_dict(cls, value: dict) -> datetime:
        if not isinstance(value, dict):
            return value
        if "$date" not in value:
            raise ValueError("Unexpected date format!")
        py_timestamp = int(value["$date"]["$numberLong"])
        return datetime.fromtimestamp(py_timestamp / 1000)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {}
        json_encoders = {
            datetime: lambda v: {"$date": {"$numberLong": int(v.timestamp() * 1000)}},
        }


class SleepDB(DbObject, SleepBase):
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: lambda v: str(v)}


class SleepList(BaseModel):
    sleep_items: list[SleepDB]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: lambda v: str(v)}

from datetime import datetime
from pydantic import BaseModel, Field, validator
from bson.objectid import ObjectId
from .db_object import DbObject


j = {
    "_id": {"$oid": "640a17f89d770e182aced59a"},
    "sleep_duration": {"$numberInt": "389"},
    "activities": [
        {"activity": "meditation", "duration": 20, "timing": 3},
        {"activity": "ice_bath", "duration": 20, "timing": 2},
        {"activity": "supplements", "amount": 200, "timing": 1},
        {"activity": "relax", "timing": 4},
    ],
    "createdAt": {"$date": {"$numberLong": "1678383096251"}},
    "__v": {"$numberInt": "0"},
}


class JournalBase(BaseModel):
    id: str | None = Field(alias="_id")
    sleep_duration: int
    activities: list[dict]
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
        json_encoders = {
            datetime: lambda v: {"$date": {"$numberLong": int(v.timestamp() * 1000)}},
        }


class JournalDB(DbObject, JournalBase):
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: lambda v: str(v),
            datetime: lambda v: {"$date": {"$numberLong": int(v.timestamp() * 1000)}},
        }


class JournalList(BaseModel):
    journal_items: list[JournalDB]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: lambda v: str(v)}

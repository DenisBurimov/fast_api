import enum
from pydantic import BaseModel, Field, validator
from bson.objectid import ObjectId

from .db_object import DbObject


"""
{"_id":{"$oid":"640a17f89d770e182aced59a"},
"activities": [
    {"activity": "meditation", "value": 20, "timing": 1},
    {"activity": "ice_bath", "value": 20, "timing": 0},
    {"activity": "supplements", "value": 200, "timing": 2},
    {"activity": "cold_shower", "timing": 2}
 ]
// activities: [
    "meditation",
    "caffeine",
    "workout",
    "breathwork",
    "cold_shower",
    "ice_bath",
    "hot_tub",
    "sauna",
    "marijuana",
    "psychedelics",
    "alcohol",
    "nicotine",
    "travel",
    "meal"
    ] //ENUM SUIT
"createdAt":{"$date":{"$numberLong":"1678383096251"}}, // automatically created by MongoDB
"__v":{"$numberInt":"0"}}
"""


class LogBookActivity(str, enum.Enum):
    meditation = "meditation"
    caffeine = "caffeine"
    workout = "workout"
    breathwork = "breathwork"
    cold_shower = "cold_shower"
    ice_bath = "ice_bath"
    hot_tub = "hot_tub"
    sauna = "sauna"
    marijuana = "marijuana"
    psychedelics = "psychedelics"
    alcohol = "alcohol"
    nicotine = "nicotine"
    travel = "travel"
    meal = "meal"


class LogBookActivityItem(BaseModel):
    activity: LogBookActivity
    value: int
    timing: int


class JournalBase(BaseModel):
    activities: list[LogBookActivityItem]
    createdAt: str | None
    v: int | None = Field(alias="__v")

    @validator("v", pre=True)
    def v_from_dict(cls, value: dict):
        if not isinstance(value, dict):
            return value
        return value.get("$numberInt")

    class Config:
        allow_population_by_field_name = True


class JournalDB(DbObject, JournalBase):
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: lambda v: str(v)}


class JournalList(BaseModel):
    journal_items: list[JournalDB]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: lambda v: str(v)}

from datetime import datetime
from pydantic import BaseModel, Field, validator
from bson.objectid import ObjectId
from .db_object import DbObject


class BurnBase(BaseModel):
    id: str | None = Field(alias="_id")
    burn_values: list[float]
    created_at: datetime = Field(alias="createdAt")
    v: int = Field(alias="__v")

    @validator("id", pre=True)
    def id_from_dict(cls, value: dict) -> str:
        if not isinstance(value, dict):
            return value
        return value.get("$oid")

    @validator("burn_values", pre=True)
    def burn_values_from_str(cls, value: str) -> list[float]:
        if isinstance(value, str):
            return [float(v.strip()) for v in value.strip("[] ").split(",")]
        return value

    @validator("created_at", pre=True)
    def created_at_from_dict(cls, value: dict) -> datetime:
        if not isinstance(value, dict):
            return value
        if "$date" not in value:
            raise ValueError("Unexpected date format!")

        py_timestamp = int(value["$date"]["$numberLong"])

        return datetime.fromtimestamp(py_timestamp / 1000)

    @validator("v", pre=True)
    def v_from_dict(cls, value: dict):
        if not isinstance(value, dict):
            return value
        return value.get("$numberInt")

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": {"$oid": "640a17f89d770e182aced59a"},
                "burn_values": "[0.7, -0.9, 1.1, -0.5]",
                "createdAt": {"$date": {"$numberLong": "1678383096251"}},
                "__v": {"$numberInt": "0"},
            }
        }
        json_encoders = {
            datetime: lambda v: {"$date": {"$numberLong": int(v.timestamp() * 1000)}},
        }


class BurnDB(DbObject, BurnBase):
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: lambda v: str(v)}


class BurnList(BaseModel):
    burn_items: list[BurnDB]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: lambda v: str(v)}

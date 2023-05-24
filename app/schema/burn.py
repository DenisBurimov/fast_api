from pydantic import BaseModel, Field
from bson.objectid import ObjectId

from .db_object import DbObject


class BurnBase(BaseModel):
    burn_values: str
    created_at: dict = Field(alias="createdAt")
    # sessionInfo: str
    # timeStamps: dict[str, Union[str, int, float]]
    # deviceInfo: dict[str, Union[str, int, float]]
    # leftPupilInfo: list[dict]
    # rightPupilInfo: list[dict]
    # leftBlinkInfo: dict[str, Union[list, int]]
    # rightBlinkInfo: dict[str, Union[list, int]]

    class Config:
        allow_population_by_field_name = True
        schema_extra = {}


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

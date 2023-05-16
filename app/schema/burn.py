from typing import Union
from pydantic import BaseModel
from bson.objectid import ObjectId

from .db_object import DbObject


class BurnBase(BaseModel):
    burn_data: dict[str, Union[str, list, dict]]


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

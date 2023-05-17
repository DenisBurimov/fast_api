from pydantic import BaseModel
from bson.objectid import ObjectId

from .db_object import DbObject


class Answer(BaseModel):
    id: int
    answered: bool
    level: int


class JournalBase(BaseModel):
    answers: list[Answer]


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

from pydantic import BaseModel, EmailStr, Field
from bson.objectid import ObjectId

from .object_id import PyObjectId


class User(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserOutput(BaseModel):
    id: str
    username: str
    email: EmailStr
    password_hash: str
    
    
class UserDB(BaseModel):
    id: PyObjectId | None = Field(default_factory=PyObjectId, alias="_id")
    username: str
    email: EmailStr
    password_hash: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Users(BaseModel):
    users: list[UserOutput]

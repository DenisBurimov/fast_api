from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator
from bson.objectid import ObjectId

from .db_object import DbObject


class UserBase(BaseModel):
    id: str | None = Field(alias="_id")
    email: EmailStr  # V
    firstname: str = Field(alias="firstName")  # To remove?
    lastname: str = Field(alias="lastName")  # To remove?
    age: int  # V
    expectations: list  # V
    gender: int  # V
    created_at: datetime | None
    updated_at: datetime | None

    @validator("id", pre=True)
    def id_from_dict(cls, value: dict):
        if not isinstance(value, dict):
            return value
        return value.get("$oid")

    @validator("age", pre=True)
    def age_from_dict(cls, value: dict):
        if not isinstance(value, dict):
            return value
        return value.get("$numberInt")

    @validator("gender", pre=True)
    def gender_from_dict(cls, value: dict):
        if not isinstance(value, dict):
            return value
        return value.get("$numberInt")

    @validator("expectations", pre=True)
    def expectations_from_list(cls, value: list):
        if not isinstance(value, list) or not isinstance(value[0], dict):
            return value

        return [value[0].get("$numberInt"), value[1].get("$numberInt")]


class UserCreate(UserBase):
    password: str
    password_hash: str = ""


class UserLogin(BaseModel):
    """fields should match to properties of OAuth2PasswordRequestForm"""

    username: str
    password: str


class UserUpdate(BaseModel):
    username: str | None
    email: EmailStr | None
    password: str | None
    firstname: str | None
    lastname: str | None
    age: int | None
    expectations: list | None
    gender: int | None


class UserDB(DbObject, UserBase):
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: lambda v: str(v)}


class UserDbWithPasswd(UserDB):
    password_hash: str


class UserList(BaseModel):
    users: list[UserDB]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: lambda v: str(v)}

import enum

from pydantic import BaseModel, EmailStr
from bson.objectid import ObjectId

from .db_object import DbObject


class UsersExpectations(str, enum.Enum):
    sleep = "sleep"
    energetic = "energetic"
    productivity = "productivity"
    stress = "stress"
    distractions = "distractions"


class UsersGender(str, enum.Enum):
    male = "male"
    female = "female"
    nonBinary = "nonBinary"
    other = "other"


class UserBase(BaseModel):
    username: str
    email: EmailStr
    firstname: str
    lastname: str
    age: int
    expectations: UsersExpectations
    gender: UsersGender


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
    expectations: UsersExpectations | None
    gender: UsersGender | None


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

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


# {"_id":{"$oid":"640a17f89d770e182aced59a"},
# "email":"bla0@a.pl",
# "password":"$2b$10$Ce1nP/Mq.REL8WfaWgSxsOTvR2Z5I.ekr4lrJpleG2asmYLo7WsUq",
# "firstName":"Krzysztof",
# "lastName":"Sobol",
# "age":{"$numberInt":"29"},
# "expectations":[{"$numberInt":"0"},{"$numberInt":"1"}],
# "gender":{"$numberInt":"0"},
# "actvities": "['x', 'y', 'z']"
# "createdAt":{"$date":{"$numberLong":"1678383096251"}},
# "updatedAt":{"$date":{"$numberLong":"1678383096251"}},
# "__v":{"$numberInt":"0"}}


class UserBase(BaseModel):
    username: str  # V
    email: EmailStr  # V
    firstname: str  # To remove
    lastname: str  # To remove
    age: int  # V
    expectations: UsersExpectations  # V
    gender: UsersGender  # V

    # To add:
    # created_at
    # upated_at


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

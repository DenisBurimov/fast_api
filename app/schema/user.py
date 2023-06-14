import enum

from pydantic import BaseModel, EmailStr
from bson.objectid import ObjectId

from .db_object import DbObject


class UserActivities(str, enum.Enum):
    caffeine = "caffeine"
    meditation = "meditation"
    supplements = "supplements"
    alcohol = "alcohol"
    coldhotTherapy = "coldhotTherapy"
    marijuana = "marijuana"


class UsersGoals(str, enum.Enum):
    enhancedFocus = "enhancedFocus"
    betterSleep = "betterSleep"
    mindfullness = "mindfulness"
    breakHabits = "breakHabits"
    removeDistractions = "removeDistractions"
    marijuana = "marijuana"


class UserBase(BaseModel):
    email: EmailStr
    name: str
    activities: list[UserActivities] | None = []
    goals: list[UsersGoals] | None = []


class UserOut(BaseModel):
    email: EmailStr
    name: str
    activities: list[UserActivities]
    goals: list[UsersGoals]


class UserCreate(UserBase):
    password: str
    password_hash: str = ""


class UserLogin(BaseModel):
    """fields should match to properties of OAuth2PasswordRequestForm"""

    username: str
    password: str


class UserUpdate(BaseModel):
    email: EmailStr | None
    name: str | None
    password: str | None
    activities: list[UserActivities] | None
    goals: list[UsersGoals] | None


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

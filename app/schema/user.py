import enum
from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr, validator
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
    created_at: str | None = None
    updated_at: str | None = None

    @validator("created_at", "updated_at", pre=True, always=True)
    def set_created_updated(cls, v):
        return v or datetime.now(timezone.utc).isoformat()


class UserOut(BaseModel):
    email: EmailStr
    name: str
    activities: list[UserActivities]
    goals: list[UsersGoals]
    v: int | None
    created_at: str | None = None
    updated_at: str | None = None


class UserCreate(UserBase):
    password: str
    password_hash: str | None = ""
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "name": "string",
                "activities": [],
                "goals": [],
                "password": "string",
                "password_hash": ""
            }
        }


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
    v: int | None
    updated_at: str | None = None
    
    @validator("updated_at", pre=True, always=True)
    def set_updated(cls, v):
        return v or datetime.now(timezone.utc).isoformat()


class UserDB(DbObject, UserBase):
    v: int | None = 0

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

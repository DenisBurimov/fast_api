from pydantic import BaseModel, EmailStr


class User(BaseModel):
    username: str
    email: EmailStr
    password: str


class Users(BaseModel):
    users: list[User]


class UserLogin(BaseModel):
    user_id: str
    password: str


class UserDB(BaseModel):
    username: str
    email: EmailStr
    password_hash: str

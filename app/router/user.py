from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database
from bson.objectid import ObjectId
from app import get_db
import app.schema as s

# from app.dependency import get_current_user

user_router = APIRouter(prefix="/user", tags=["Users"])


@user_router.get("/all", response_model=s.Users)
def get_users(db: Database = Depends(get_db)):
    collection = db.users.find()
    users = []
    for obj in collection:
        user = s.UserOutput(
            id=str(obj.get("id")),
            username=obj.get("username"),
            email=obj.get("email"),
            password_hash=obj.get("password_hash"),
        )
        users.append(dict(user))
    return s.Users(users=users)


@user_router.get("/{id}", response_model=s.UserOutput)
def get_user_by_id(
    id: str,
    db: Database = Depends(get_db),
    # current_user: int = Depends(get_current_user),
):
    user = db.users.find_one({"id": ObjectId(id)})
    if not user:
        raise HTTPException(status_code=404, detail="This user was not found")

    return s.UserOutput(
        id=str(user.get("id")),
        username=user.get("username"),
        email=user.get("email"),
        password_hash=user.get("password_hash"),
    )


@user_router.put("/{id}", response_model=s.UserOutput)
def get_update_user(
    id: str,
    db: Database = Depends(get_db),
    # current_user: int = Depends(get_current_user),
):
    user = db.users.find_one({"id": ObjectId(id)})
    if not user:
        raise HTTPException(status_code=404, detail="This user was not found")

    data = s.UserDB(
        id=ObjectId(id),
        username="New Username",
        email=user.get("email"),
        password_hash=user.get("password_hash"),
    ).dict()

    # db.users.update_one({"id": ObjectId(id)}, {"$set": {"username": "New Username"}})
    db.users.update_one({"id": ObjectId(id)}, {"$set": data})

    return s.UserOutput(
        id=str(user.get("id")),
        username=user.get("username"),
        email=user.get("email"),
        password_hash=user.get("password_hash"),
    )


@user_router.delete("/{id}", response_model=s.DeleteMessage)
def get_delete_user(
    id: str,
    db: Database = Depends(get_db),
    # current_user: int = Depends(get_current_user),
):
    user = db.users.delete_one({"id": ObjectId(id)})
    if not user:
        raise HTTPException(status_code=404, detail="This user was not found")

    message = f"User {id} was successfully deleted"
    return s.DeleteMessage(message=message)

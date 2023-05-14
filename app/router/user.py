from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database
from pymongo import results
from bson.objectid import ObjectId
from app import get_db
import app.schema as s

# from app.dependency import get_current_user

user_router = APIRouter(prefix="/user", tags=["User", "UserList"])


@user_router.get("/all", response_model=s.UserList)
def get_users(db: Database = Depends(get_db)):
    return s.UserList(users=[s.UserDB.parse_obj(o) for o in db.users.find()])


@user_router.get("/{id}", response_model=s.UserDB)
def get_user_by_id(
    id: str,
    db: Database = Depends(get_db),
    # current_user: int = Depends(get_current_user),
):
    user = db.users.find_one({"_id": ObjectId(id)})
    if not user:
        raise HTTPException(status_code=404, detail="This user was not found")

    return s.UserDB.parse_obj(user)


@user_router.put("/{id}", response_model=s.UserDB)
def get_update_user(
    id: str,
    data: s.UserUpdate,
    db: Database = Depends(get_db),
    # current_user: int = Depends(get_current_user),
):
    db.users.update_one({"_id": ObjectId(id)}, {"$set": data.dict(exclude_none=True)})

    return s.UserDB.parse_obj(db.users.find_one({"_id": ObjectId(id)}))


@user_router.delete("/{id}", response_model=s.DeleteMessage)
def get_delete_user(
    id: str,
    db: Database = Depends(get_db),
    # current_user: int = Depends(get_current_user),
):
    res: results.DeleteResult = db.users.delete_one({"_id": ObjectId(id)})
    if not res.deleted_count:
        raise HTTPException(status_code=404, detail="This user was not found")

    message = f"User {id} was successfully deleted"
    return s.DeleteMessage(message=message)

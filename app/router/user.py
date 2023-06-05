from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database
from pymongo import results
from bson.objectid import ObjectId
from app import get_db
from app.logger import log
import app.schema as s
from app.dependency import get_current_user

user_router = APIRouter(prefix="/user", tags=["User"])


@user_router.get("/all", response_model=s.UserList)
def get_users(
    db: Database = Depends(get_db),
    _: s.UserDB = Depends(get_current_user),
):
    """
    Args:
        db (Database, optional): db generator.
        _ (s.UserDB, optional): Requires logged in user.

    Returns:
        schema.UserList class with users field, which is a list of UserDB classes.
    """
    users_list = s.UserList(users=[s.UserDB.parse_obj(o) for o in db.users.find()])
    if not users_list.users:
        log(log.ERROR, "Users not found")
    log(log.INFO, "[%d] users have been fetched", len(users_list.users))
    return users_list


@user_router.get("/{id}", response_model=s.UserDB)
def get_user_by_id(
    id: str,
    db: Database = Depends(get_db),
    _: s.UserDB = Depends(get_current_user),
):
    """
    Args:
        id (str): String with users id (not an ObjectID!).
        db (Database, optional): db generator.
        _ (s.UserDB, optional): Requires logged in user.

    Raises:
        HTTPException: in case if user with given id was not found.

    Returns:
        schema.UserDB with a given id, parsed by pydantic from the mongo object.
    """
    user = db.users.find_one({"_id": ObjectId(id)})
    if not user:
        log(log.ERROR, "User with id [%s] was not found", id)
        raise HTTPException(status_code=404, detail="This user was not found")

    log(log.INFO, "User [%s]: %s", id, user)
    return s.UserDB.parse_obj(user)


@user_router.put("/{id}", response_model=s.UserDB)
def get_update_user(
    id: str,
    data: s.UserUpdate,
    db: Database = Depends(get_db),
    _: s.UserDB = Depends(get_current_user),
):
    user_update = db.users.update_one(
        {"_id": ObjectId(id)}, {"$set": data.dict(exclude_none=True)}
    )
    if not user_update.acknowledged:
        log(log.ERROR, "Something went wrong. Cannot update user [%s]", id)

    log(log.INFO, "User [%s] has been successfully updated", id)
    return s.UserDB.parse_obj(db.users.find_one({"_id": ObjectId(id)}))


@user_router.delete("/{id}", response_model=s.DeleteMessage)
def get_delete_user(
    id: str,
    db: Database = Depends(get_db),
    _: s.UserDB = Depends(get_current_user),
):
    res: results.DeleteResult = db.users.delete_one({"_id": ObjectId(id)})
    if not res.deleted_count:
        log(log.ERROR, "User [%s] was not found", id)
        raise HTTPException(status_code=404, detail="This user was not found")

    log(log.INFO, "User [%s] was successfully deleted", id)
    message = f"User {id} was successfully deleted"
    return s.DeleteMessage(message=message)

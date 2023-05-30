from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from pymongo.database import Database
from pymongo import results
from bson.objectid import ObjectId
from app import get_db, hash_verify, make_hash
import app.schema as s
from app.logger import log

from app.oauth2 import create_access_token

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post("/login", response_model=s.Token)
def username(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Database = Depends(get_db),
):
    """
    Args:
        user_credentials: OAuth2PasswordRequestForm.
        db: database generator.

    Raises:
        HTTPException: if doesn't find name or email or they don't match with password

    Returns:
        Session token if the auth with name or email was successful
    """
    res = db.users.find_one(
        {
            "$or": [
                {"name": user_credentials.username},
                {"email": user_credentials.username},
            ]
        }
    )
    user = s.UserDbWithPasswd.parse_obj(res) if res else None
    if not user or not hash_verify(user_credentials.password, user.password_hash):
        log(log.ERROR, "User [%s] was not authenticated", user_credentials.username)
        raise HTTPException(status_code=403, detail="Invalid credentials")

    access_token = create_access_token(data={"user_id": str(user.id)})
    log(
        log.ERROR,
        "User [%s] has been successfully authenticated",
        user_credentials.username,
    )

    return s.Token(
        access_token=access_token,
        token_type="Bearer",
    )


@auth_router.post(
    "/sign-up",
    status_code=status.HTTP_201_CREATED,
    response_model=s.UserDB,
)
def sign_up(
    data: s.UserCreate,
    db: Database = Depends(get_db),
):
    """
    Args:
        data (s.UserCreate): validated by pydantic user credentials.
        db (Database, optional): db generator.

    Returns:
        schema.UserDB class that parses a new db user's instance.
    """
    user = db.users.find_one({"_id": ObjectId(data.id)})
    if user:
        log(log.ERROR, "User with id [%s] already exists", data.id)
        raise HTTPException(status_code=409, detail="User already exists")

    data.password_hash = make_hash(data.password)
    res: results.InsertOneResult = db.users.insert_one(
        # We can't just pass data.dict() because mongo will give the new instance a new random id
        {
            "_id": ObjectId(data.id),
            "name": data.name,
            "email": data.email,
            "age": data.age,
            "expectations": data.expectations,
            "gender": data.gender,
            "created_at": data.created_at,
            "updated_at": data.updated_at,
            "password_hash": data.password_hash,
        }
    )

    log(log.INFO, "User [%s] signed up", data.email)
    return s.UserDB.parse_obj(db.users.find_one({"_id": res.inserted_id}))

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from pymongo.database import Database
from pymongo import results
from app.dependency import get_current_user_by_refresh_token
from app import get_db, hash_verify, make_hash
import app.schema as s
from app.logger import log

from app.oauth2 import create_access_token, create_refresh_token

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post("/login", response_model=s.Tokens)
def username(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Database = Depends(get_db),
):
    """ """
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

    user_details = s.Tokens(
        access_token=create_access_token(data={"user_id": str(user.id)}),
        refresh_token=create_refresh_token(
            data={"user_id": str(user.id), "password_hash": user.password_hash}
        ),
        token_type="Bearer",
        id = str(user.id),
        created_at = user.created_at
    )
    
    return user_details


@auth_router.post("/refresh", response_model=s.Tokens)
def refresh(
    db: Database = Depends(get_db),
    current_user: s.UserDB = Depends(get_current_user_by_refresh_token),
):
    """ """
    res = db.users.find_one({"_id": current_user.id})
    user = s.UserDbWithPasswd.parse_obj(res) if res else None
    tokens = s.Tokens(
        access_token=create_access_token(data={"user_id": str(current_user.id)}),
        refresh_token=create_refresh_token(
            data={"user_id": str(current_user.id), "password_hash": user.password_hash}
        ),
        token_type="Bearer",
    )

    return tokens


@auth_router.post(
    "/sign-up",
    status_code=status.HTTP_201_CREATED,
    response_model=s.UserDB,
)
def sign_up(
    data: s.UserCreate,
    db: Database = Depends(get_db),
):
    res = db.users.find_one(
        (
            {"email": data.email}
        )
    )  
    if res:
        log(log.ERROR, "User [%s] already exists", data.email)
        raise HTTPException(status_code=400, detail="User already exists")
    
    data.password_hash = make_hash(data.password)
    res: results.InsertOneResult = db.users.insert_one(
        data.dict(exclude={"password": True})
    )

    log(log.INFO, "User [%s] signed up", data.email)
    return s.UserDB.parse_obj(db.users.find_one({"_id": res.inserted_id}))

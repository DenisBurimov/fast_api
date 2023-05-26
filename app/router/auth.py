from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from pymongo.database import Database
from pymongo import results

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
    data.password_hash = make_hash(data.password)
    res: results.InsertOneResult = db.users.insert_one(
        data.dict(exclude={"password": True})
    )

    log(log.INFO, "User [%s] signed up", data.email)
    return s.UserDB.parse_obj(db.users.find_one({"_id": res.inserted_id}))

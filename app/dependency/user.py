from bson.objectid import ObjectId

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from pymongo.database import Database
from app.logger import log
from app.oauth2 import verify_access_token, decode_refresh_token, INVALID_REFRESH_TOKEN
from app.database import get_db
import app.schema as s

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Database = Depends(get_db),
) -> s.UserDB:
    token: s.TokenData = verify_access_token(token)
    return s.UserDB.parse_obj(db.users.find_one({"_id": ObjectId(token.user_id)}))


def get_current_user_by_refresh_token(
    token: str = Depends(oauth2_scheme),
    db: Database = Depends(get_db),
) -> s.UserDB:
    token: s.RefreshTokenData = decode_refresh_token(token)
    user_db = db.users.find_one({"_id": ObjectId(token.user_id)})
    user = s.UserDbWithPasswd.parse_obj(user_db) if user_db else None

    if not user or not (token.password_hash == user.password_hash):
        log(log.ERROR, "User [%s] was not authenticated", user.name)
        raise INVALID_REFRESH_TOKEN
    return user

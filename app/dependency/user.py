from bson.objectid import ObjectId

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from pymongo.database import Database

from app.oauth2 import verify_access_token, INVALID_CREDENTIALS_EXCEPTION
from app.database import get_db
import app.schema as s

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Database = Depends(get_db),
) -> s.UserDB:
    token: s.TokenData = verify_access_token(token, INVALID_CREDENTIALS_EXCEPTION)
    return s.UserDB.parse_obj(db.users.find_one({"_id": ObjectId(token.user_id)}))

from datetime import datetime, timedelta
from fastapi import status
from jose import JWTError, jwt
from fastapi import HTTPException

import app.schema as s
from app.config import Settings, get_settings

settings: Settings = get_settings()

INVALID_CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

NEED_REFRESH_TOKEN = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Access token has expired",
    headers={"WWW-Authenticate": "Bearer"},
)

INVALID_REFRESH_TOKEN = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid refresh token. Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt_access_token = jwt.encode(to_encode, settings.JWT_SECRET)

    return encoded_jwt_access_token


def verify_access_token(token: str) -> s.TokenData:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET)
        id: str = payload.get("user_id")

        if not id:
            raise INVALID_CREDENTIALS_EXCEPTION

        token_data = s.TokenData(user_id=id)
    except JWTError:
        raise NEED_REFRESH_TOKEN

    return token_data


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})

    encoded_jwt_refresh_token = jwt.encode(to_encode, settings.JWT_SECRET)

    return encoded_jwt_refresh_token


def verify_refresh_token(token: str) -> s.RefreshTokenData:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET)
        id: str = payload.get("user_id")
        password_hash: str = payload.get("password_hash")

        if not id:
            raise INVALID_CREDENTIALS_EXCEPTION

        token_data = s.RefreshTokenData(
            user_id=id,
            password_hash=password_hash,
        )
    except JWTError:
        raise INVALID_REFRESH_TOKEN

    return token_data

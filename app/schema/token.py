from pydantic import BaseModel


class Tokens(BaseModel):
    access_token: str
    refresh_token: str | None
    token_type: str
    id: str | None = None
    created_at: str | None = None


class TokenData(BaseModel):
    user_id: str = None


class RefreshTokenData(BaseModel):
    user_id: str = None
    password_hash: str = None

from pydantic import BaseModel


class Token(BaseModel):
    token: str
    token_type: str


class TokenData(BaseModel):
    user_id: str = None


class RefreshTokenData(BaseModel):
    user_id: str = None
    password_hash: str = None


class AuthTokens(BaseModel):
    access_token: Token
    refresh_token: Token

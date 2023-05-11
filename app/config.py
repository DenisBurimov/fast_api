from functools import lru_cache
from pydantic import BaseSettings, EmailStr


class Settings(BaseSettings):
    JWT_SECRET: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ADMIN_USER: str = "admin"
    ADMIN_PASS: str = "admin"
    ADMIN_EMAIL: EmailStr = "admin@admin.com"
    MONGO_URI: str
    MONGO_DB: str

    class Config:
        env_file = ["project.env", ".env"]


@lru_cache
def get_settings() -> Settings:
    return Settings()

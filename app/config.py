from functools import lru_cache
from pydantic import BaseSettings, EmailStr


class Settings(BaseSettings):
    ENV_MODE: str
    JWT_SECRET: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ACCESS_TOKEN_EXPIRE_DAYS: int
    ADMIN_USER: str = "admin"
    ADMIN_PASS: str = "admin"
    ADMIN_EMAIL: EmailStr = "admin@admin.com"
    MONGO_URI: str
    MONGO_DB: str
    MONGO_INITDB_ROOT_USERNAME: str
    MONGO_INITDB_ROOT_PASSWORD: str
    MONGO_HOST: str
    MONGO_PORT: int
    BURN_MODEL_URL: str
    BURN_MODEL_URL_LOCAL: str
    SLEEP_MODEL_URL: str
    SLEEP_MODEL_URL_LOCAL: str
    AWS_ACCESS_KEY: str
    AWS_SECRET_KEY: str

    class Config:
        env_file = ["project.env", ".env"]


@lru_cache
def get_settings() -> Settings:
    return Settings()

from typing import Generator

from pymongo import MongoClient
from pymongo.database import Database
from app.config import Settings, get_settings

settings: Settings = get_settings()

mongo = MongoClient(settings.MONGO_URI)


def get_db() -> Generator[Database, None, None]:
    # TODO: begin transaction
    yield mongo[settings.MONGO_DB]
    # TODO: end transaction

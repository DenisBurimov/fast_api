from pymongo import MongoClient
from app.config import Settings, get_settings

settings: Settings = get_settings()

db = MongoClient(settings.DB_URI)


def get_db():
    yield db

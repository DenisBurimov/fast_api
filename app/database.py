from typing import Generator

from pymongo import MongoClient
from pymongo.database import Database

from .config import get_settings

import certifi

settings = get_settings()

MONGO_HOST = settings.MONGO_HOST
MONGO_PORT = settings.MONGO_PORT
MONGO_INITDB_ROOT_USERNAME = settings.MONGO_INITDB_ROOT_USERNAME
MONGO_INITDB_ROOT_PASSWORD = settings.MONGO_INITDB_ROOT_PASSWORD
# mongo = MongoClient(host=["mongo"], username="user", password="pass")
# mongo = MongoClient(
#     host=[MONGO_HOST],
#     username=MONGO_INITDB_ROOT_USERNAME,
#     password=MONGO_INITDB_ROOT_PASSWORD,
# )
mongo = MongoClient(settings.MONGO_URI, tlsCAFile=certifi.where())

def get_db() -> Generator[Database, None, None]:
    # TODO: begin transaction
    yield mongo[settings.MONGO_DB]
    # TODO: end transaction

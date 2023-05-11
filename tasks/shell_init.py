# flake8: noqa F401
from app.database import mongo, get_db

db = next(get_db())

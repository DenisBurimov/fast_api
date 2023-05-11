from pymongo import MongoClient
from app.config import Settings, get_settings
from app.main import app

settings: Settings = get_settings()

# db = MongoClient(settings.MONGO_URI)


# @app.on_event("startup")
# def startup_db_client():
#     app.mongodb_client = MongoClient(settings.MONGO_URI)
#     app.database = app.mongodb_client["oculo"]


# @app.on_event("shutdown")
# def shutdown_db_client():
#     app.mongodb_client.close()


# def get_db():
#     yield db

# flake8: noqa F402
from fastapi import FastAPI
from pymongo import MongoClient
from app.router import router
from app.config import Settings, get_settings

settings = get_settings()


app = FastAPI()
app.include_router(router)


@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient(settings.MONGO_URI)
    app.database = app.mongodb_client["oculo"]


@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()


@app.get("/")
def root():
    return {"message": "Hello", "env_var": settings.MONGO_URI}

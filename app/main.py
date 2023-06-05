# flake8: noqa F402
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from pymongo import MongoClient
from app.router import router
from app.config import Settings, get_settings

settings: Settings = get_settings()


app = FastAPI()
app.include_router(router)


@app.get("/")
def root():
    return RedirectResponse("/docs", status_code=303)

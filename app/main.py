# flake8: noqa F402
from fastapi import FastAPI
from app.router import router


app = FastAPI()
app.include_router(router)


@app.get("/")
def root():
    return {"message": "Hello"}

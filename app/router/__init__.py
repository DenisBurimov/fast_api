# flake8: noqa F401
from fastapi import APIRouter, Request

from .auth import auth_router
from .user import user_router
from .sleep import sleep_router
from .burn import burn_router
from .logbook import logbook_router

router = APIRouter(prefix="/api", tags=["API"])

router.include_router(auth_router)
router.include_router(user_router)
router.include_router(sleep_router)
router.include_router(burn_router)
router.include_router(logbook_router)


@router.get("/list-endpoints/")
def list_endpoints(request: Request):
    url_list = [
        {"path": route.path, "name": route.name} for route in request.app.routes
    ]
    return url_list

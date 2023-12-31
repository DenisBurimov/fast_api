from invoke import task

from app.logger import log
from app import get_db, get_settings, make_hash
from app import schema as s

db = next(get_db())
cfg = get_settings()


@task
def create_superuser(_):
    """Adds admin(default) user"""

    if db["user"].find_one({"email": cfg.ADMIN_EMAIL}):
        log(log.WARNING, "SuperUser -%s already exists", cfg.ADMIN_EMAIL)
    else:
        user = s.UserDB(
            username=cfg.ADMIN_USER,
            email=cfg.ADMIN_EMAIL,
            password_hash=make_hash(cfg.ADMIN_PASS),
            name=cfg.ADMIN_USER,
            age=30,
            expectations="sleep",
            gender="male",
        )
        db["users"].insert_one(user.dict())
        log(log.INFO, "SuperUser %s created", cfg.ADMIN_EMAIL)

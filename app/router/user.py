from fastapi import APIRouter, Request  # HTTPException, Depends
import app.schema as s

# from app.database import get_db

# from app.dependency import get_current_user

user_router = APIRouter(prefix="/user", tags=["Users"])


# @user_router.post("/", status_code=201, response_model=s.User)
# def create_user(user: s.User, db=Depends(get_db)):
#     # new_user = m.User(**user.dict())
#     # db.add(new_user)
#     # db.commit()
#     # db.refresh(new_user)

#     return  # new_user


@user_router.get(
    "/",
    # response_model=s.Users,
)
def get_users(
    request: Request,
    # db=Depends(get_db),
    # current_user: int = Depends(get_current_user),
):
    collection = request.app.database["user"].find()
    users = list(collection)
    # cursor = db.local.user.find()
    # users = [s.User(**x) for x in cursor]
    return users


# @user_router.get("/{id}", response_model=s.User)
# def get_user(
#     id: int,
#     db=Depends(db),
#     # current_user: int = Depends(get_current_user),
# ):
#     user = db.query(m.User).get(id)

#     if not user:
#         raise HTTPException(status_code=404, detail="This user was not found")

#     return user

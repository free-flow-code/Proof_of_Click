from fastapi import APIRouter, Response, Depends

from app.users.schemas import SUserAuth
from app.users.models import Users
from app.users.dao import UsersDAO
from app.users.auth import authenticate_user, add_user, create_access_token
from app.users.dependencies import get_current_user
from app.exceptions import IncorrectEmailOrPasswordException, AccessDeniedException, ObjectNotFoundException


router = APIRouter(
    prefix="/auth",
    tags=["Auth & Users"]
)


@router.post("/register")
async def register_user(user_data: SUserAuth):
    await add_user(user_data)
    return {"detail": "User register successfully"}


@router.post("/register/{referral_link}")
async def register_ref_user(user_data: SUserAuth, referral_link: str):
    await add_user(user_data, referral_link)
    return {"detail": "User register successfully"}


@router.post("/login")
async def login_user(response: Response, user_data: SUserAuth):
    user = await authenticate_user(user_data.mail, user_data.password)
    if not user:
        raise IncorrectEmailOrPasswordException
    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie("poc_access_token", access_token, httponly=True)
    return {"access_token": access_token}


@router.post("/logout")
async def logout_user(response: Response):
    response.delete_cookie("poc_access_token")
    return {"detail": "User logout"}


@router.get("/me")
async def get_current_user_me(current_user: Users = Depends(get_current_user)):
    user = dict(current_user)
    user.pop("hash_password", None)
    user.pop("last_update_time", None)
    return user


@router.delete("/{user_id}")
async def delete_user(user_id: int, current_user: Users = Depends(get_current_user)):
    if current_user.role.value != "admin":
        raise AccessDeniedException

    user = await UsersDAO.find_one_or_none(id=user_id)
    print(user_id, user)
    if not user:
        raise ObjectNotFoundException

    await UsersDAO.delete(user_id)
    return {"detail": "User deleted successfully"}

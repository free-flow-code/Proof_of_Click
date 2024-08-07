import logging

from fastapi import APIRouter, Response, Depends, HTTPException, status

from app.config import settings
from app.users.schemas import SUserAuth, SUserLogin, SRestorePassword
from app.users.models import Users
from app.users.dao import UsersDAO
from app.users.auth import authenticate_user, add_user, create_access_token, get_password_from_hash
from app.users.dependencies import get_current_user
from app.tasks.tasks import send_verify_code_to_email, send_restore_password_to_email
from app.exceptions import (
    IncorrectEmailOrPasswordException,
    AccessDeniedException,
    ObjectNotFoundException,
    IncorrectEmailCodeException
)


router = APIRouter(
    prefix="/auth",
    tags=["Auth & Users"]
)


@router.post("/register")
async def register_user(response: Response, user_data: SUserAuth):
    created_user = await add_user(user_data)
    await login_user(response, user_data)
    send_verify_code_to_email.delay(created_user['mail_confirm_code'], user_data.mail)
    logging.info(f"User {user_data.username} registered")


@router.post("/register/{referral_link}")
async def register_ref_user(user_data: SUserAuth, referral_link: str):
    await add_user(user_data, referral_link)
    return {"detail": "User register successfully"}


@router.post("/login")
async def login_user(response: Response, user_data: SUserLogin):
    user = await authenticate_user(user_data.mail, user_data.password)
    if not user:
        raise IncorrectEmailOrPasswordException
    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie("poc_access_token", access_token, httponly=True, secure=settings.SET_COOKIE_SECURE)
    logging.info(f"User {user.username} logged in")
    return {"access_token": access_token}


@router.post("/restore_password")
async def restore_password(user_data: SRestorePassword):
    user = await UsersDAO.find_by_key(mail=user_data.mail)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email not found"
        )
    password = get_password_from_hash(user.hash_password)
    send_restore_password_to_email.delay(user.username, password, user_data.mail)
    return {"detail": f"Password send to email {user_data.mail}"}


# verify email
@router.get("/verify/{mail_confirm_code}")
async def verify_email(mail_confirm_code: int, current_user: Users = Depends(get_current_user)):
    if current_user.is_confirm_mail:
        # возвращаем исключение для перенаправления на index.html
        raise HTTPException(status_code=status.HTTP_301_MOVED_PERMANENTLY)
    if int(current_user.mail_confirm_code) != mail_confirm_code:
        raise IncorrectEmailCodeException
    await UsersDAO.edit(current_user.id, is_confirm_mail=True)
    return {"detail": "Email is verify"}


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


@router.get("/leaders")
async def get_leaders(current_user: Users = Depends(get_current_user)):
    return await UsersDAO.get_top_100_users()


@router.delete("/{user_id}")
async def delete_user(user_id: int, current_user: Users = Depends(get_current_user)):
    if current_user.role.value != "admin":
        raise AccessDeniedException

    user = await UsersDAO.find_one_or_none(id=user_id)
    if not user:
        raise ObjectNotFoundException

    await UsersDAO.delete(user_id)
    return {"detail": "User deleted successfully"}

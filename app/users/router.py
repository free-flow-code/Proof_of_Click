import logging

from fastapi import APIRouter, Response, Depends, HTTPException, status

from app.config import settings
from app.redis_init import get_redis
from app.data_processing_funcs import add_user_data_to_redis
from app.users.schemas import SUserAuth, SUserLogin, SRestorePassword
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
async def register_user(response: Response, user_data: SUserAuth, redis=Depends(get_redis)):
    created_user = await add_user(user_data)
    await login_user(response, user_data)
    await add_user_data_to_redis(created_user, redis)
    send_verify_code_to_email.delay(created_user['mail_confirm_code'], user_data.mail)
    logging.info(f"User {user_data.username} registered")


@router.post("/register/{referral_link}")  # TODO refferal_link - do it optional and delete first router?????
async def register_ref_user(response: Response, user_data: SUserAuth, referral_link: str, redis=Depends(get_redis)):
    created_user = await add_user(user_data, referral_link)
    await login_user(response, user_data)
    await add_user_data_to_redis(created_user, redis)
    send_verify_code_to_email.delay(created_user['mail_confirm_code'], user_data.mail)
    logging.info(f"User {user_data.username} registered")


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
async def verify_email(mail_confirm_code: int, current_user=Depends(get_current_user), redis=Depends(get_redis)):
    if bool(current_user["is_confirm_mail"]):
        # возвращаем исключение для перенаправления на index.html
        raise HTTPException(status_code=status.HTTP_301_MOVED_PERMANENTLY)
    if int(current_user["mail_confirm_code"]) != mail_confirm_code:
        raise IncorrectEmailCodeException

    await UsersDAO.edit(int(current_user["id"]), is_confirm_mail=True)
    await redis.hset(f"user_data:{current_user['id']}", mapping={"is_confirm_mail": "True"})
    return {"detail": "Email is verify"}


@router.post("/logout")
async def logout_user(response: Response):
    response.delete_cookie("poc_access_token")
    return {"detail": "User logout"}


@router.get("/me")
async def get_me_info(current_user=Depends(get_current_user), redis=Depends(get_redis)):
    mining_chance = {"mining_chance": await redis.get("mining_chance")}
    keys_to_send = [
        "username",
        "mail",
        "blocks_balance",
        "clicks_per_sec",
        "blocks_per_click",
        "referral_link"
    ]
    user_data = {key: current_user[key] for key in keys_to_send if key in current_user}
    user_data.update(mining_chance)
    return user_data


@router.get("/leaders")
async def get_leaders(current_user=Depends(get_current_user)):
    redis_client = await get_redis()
    top_users = await redis_client.zrevrange('users_balances', 0, 99, withscores=True)
    return list(
        map(
            lambda user_data: {"username": user_data[0], "balance": user_data[1]},
            top_users
        )
    )


@router.delete("/{user_id}")
async def delete_user(user_id: int, current_user=Depends(get_current_user), redis=Depends(get_redis)):
    if current_user["role"] != "admin":
        raise AccessDeniedException

    user = await UsersDAO.find_one_or_none(id=user_id)
    if not user:
        raise ObjectNotFoundException

    await UsersDAO.delete(user_id)
    await redis.delete(f"user_data:{user_id}")
    return {"detail": "User deleted successfully"}

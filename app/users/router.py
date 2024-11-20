from fastapi import APIRouter, Response, Depends, HTTPException, status

from app.config import settings
from app.redis_init import get_redis
from app.utils.logger_init import logger
from app.utils.users_init import add_user_data_to_redis
from app.utils.mining_chance_init import get_mining_chance_singleton
from app.utils.data_processing_funcs import get_user_data_tag_in_redis
from app.users.schemas import SUserAuth, SUserLogin, SRestorePassword
from app.users.dao import UsersDAO
from app.users.dependencies import get_current_user

from app.users.auth import (
    add_new_user_to_db,
    authenticate_user,
    create_access_token,
    get_password_from_hash
)
from app.tasks.tasks import (
    send_verify_code_to_email,
    send_restore_password_to_email
)
from app.exceptions import (
    AccessDeniedException,
    ObjectNotFoundException,
    IncorrectEmailCodeException,
    IncorrectEmailOrPasswordException
)


router = APIRouter(
    prefix="/auth",
    tags=["Auth & Users"]
)


@router.post("/register")
async def register_user(response: Response, user_data: SUserAuth):
    created_user = await add_new_user_to_db(user_data)
    await login_user(response, user_data)
    await add_user_data_to_redis(created_user, redis_ttl=3600)
    send_verify_code_to_email.delay(created_user['mail_confirm_code'], user_data.mail)
    logger.info(f"User {user_data.username} registered.")


@router.post("/register/{referral_link}")  # TODO refferal_link - do it optional and delete first router?????
async def register_ref_user(response: Response, user_data: SUserAuth, referral_link: str):
    created_user = await add_new_user_to_db(user_data, referral_link)
    await login_user(response, user_data)
    await add_user_data_to_redis(created_user, redis_ttl=3600)
    send_verify_code_to_email.delay(created_user['mail_confirm_code'], user_data.mail)
    logger.info(f"User {user_data.username} registered.")


@router.post("/login")
async def login_user(response: Response, user_data: SUserLogin):
    user = await authenticate_user(user_data.mail, user_data.password)
    if not user:
        raise IncorrectEmailOrPasswordException
    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie("poc_access_token", access_token, httponly=True, secure=settings.SET_COOKIE_SECURE)
    logger.info(f"User {user.username} logged in.")
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
    await redis.hset(
        f"user_data:{current_user['redis_tag']}:{current_user['id']}",
        mapping={"is_confirm_mail": "True"}
    )
    return {"detail": "Email is verify"}


@router.post("/logout")
async def logout_user(response: Response):
    response.delete_cookie("poc_access_token")
    return {"detail": "User logout"}


@router.get("/me")
async def get_me_info(current_user=Depends(get_current_user)):
    singleton = get_mining_chance_singleton()
    mining_chance = singleton.get_value()
    return {
        "username": current_user["username"],
        "mail": current_user["mail"],
        "blocks_balance": float(current_user["blocks_balance"]),
        "clicks_per_sec": int(float(current_user["clicks_per_sec"])),
        "blocks_per_click": float(current_user["blocks_per_click"]),
        "referral_link": current_user["referral_link"],
        "mining_chance": mining_chance
    }


@router.get("/leaders")
async def get_leaders(current_user=Depends(get_current_user)):
    redis_client = await get_redis()
    top_users = await redis_client.zrevrange('users_balances', 0, 99, withscores=True)
    return list(
        map(
            lambda user_data: {"username": user_data[0], "blocks_balance": float(user_data[1])},
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
    redis_tag = await get_user_data_tag_in_redis(user_id, redis)
    if redis_tag:
        await redis.delete(f"user_data:{redis_tag}:{user_id}")
    return {"detail": "User deleted successfully"}

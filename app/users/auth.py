import os
import string
import random
from jose import jwt
from fastapi import HTTPException
from datetime import datetime, timedelta
from passlib.context import CryptContext
from pydantic import EmailStr

from app.config import settings
from app.users.dao import UsersDAO
from app.users.schemas import SUserAuth

os.environ["PASSLIB_BUILTIN_BCRYPT"] = "enabled"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def generate_referral_link():
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(12))
    return f'{settings.DOMAIN}/auth/register/{random_string}'


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, settings.ALGORITHM
    )
    return encoded_jwt


async def authenticate_user(mail: EmailStr, password: str):
    user = await UsersDAO.find_by_key(mail=mail)
    if not user:
        return None
    if not verify_password(password, user.hash_password):
        return None
    return user


# register new user
async def add_user(user_data: SUserAuth, referral_link: str = None):
    existing_username = await UsersDAO.find_one_or_none(username=user_data.username)
    if existing_username:
        raise HTTPException(status_code=500)  # TODO
    existing_mail = await UsersDAO.find_one_or_none(mail=user_data.mail)
    if existing_mail:
        raise HTTPException(status_code=500)  # TODO

    if not referral_link:
        referer = None
    else:
        existing_ref_link = await UsersDAO.find_one_or_none(
            referral_link=f'{settings.DOMAIN}/auth/register/{referral_link}')
        if not existing_ref_link:
            raise HTTPException(status_code=500)  # TODO
        referer = existing_ref_link

    hashed_password = get_password_hash(user_data.password)
    await UsersDAO.add(
        username=user_data.username,
        mail=user_data.mail,
        hash_password=hashed_password,
        registration_date=datetime.utcnow(),
        referral_link=generate_referral_link(),
        referer=referer,
        improvements=None,
        telegram_id=None,
        last_update_time=None
    )

import string
import random
from jose import jwt
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from pydantic import EmailStr

from app.config import settings
from app.users.dao import UsersDAO
from app.users.schemas import SUserAuth
from app.utils.logger_init import logger
from app.exceptions import UsernameAlreadyExistsException, EmailAlreadyExistException

key = settings.ENCRYPTION_KEY
cipher_suite = Fernet(key)


def get_password_hash(password: str) -> str:
    encrypted_password = cipher_suite.encrypt(password.encode())
    return encrypted_password.decode()


def get_password_from_hash(encrypted_password: str) -> str:
    decrypted_password = cipher_suite.decrypt(encrypted_password.encode())
    return decrypted_password.decode()


def verify_password(plain_password, hashed_password) -> bool:
    try:
        decrypted_password = get_password_from_hash(hashed_password)
        return plain_password == decrypted_password
    except Exception as e:
        logger.info(f"Ошибка при расшифровке пароля: {e}")
        return False


def generate_referral_link():
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(12))
    return f'{settings.FRONTEND_DOMAIN}/login.html?ref={random_string}'


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_TOKEN_DELAY_MINUTES)
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
        raise UsernameAlreadyExistsException
    existing_mail = await UsersDAO.find_one_or_none(mail=user_data.mail)
    if existing_mail:
        raise EmailAlreadyExistException

    if not referral_link:
        referer = None
    else:
        referer = await UsersDAO.find_one_or_none(
            referral_link=f'{settings.FRONTEND_DOMAIN}/login.html?ref={referral_link}'
        )

    hashed_password = get_password_hash(user_data.password)
    created_user = await UsersDAO.add(
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
    return created_user

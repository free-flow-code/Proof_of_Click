from fastapi import APIRouter, Response, HTTPException, status

from app.users.schemas import SUserAuth
from app.users.auth import authenticate_user, add_user, create_access_token


router = APIRouter(
    prefix="/auth",
    tags=["Auth & Users"]
)


@router.post("/register")
async def register_user(user_data: SUserAuth):
    await add_user(user_data)


@router.post("/register/{referral_link}")
async def register_ref_user(user_data: SUserAuth, referral_link: str):
    await add_user(user_data, referral_link)


@router.post("/login")
async def login_user(response: Response, user_data: SUserAuth):
    user = await authenticate_user(user_data.mail, user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie("poc_access_token", access_token, httponly=True)
    return {"access_token": access_token}

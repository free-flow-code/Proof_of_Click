from pydantic import BaseModel, ConfigDict, EmailStr


class SUserAuth(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    mail: EmailStr
    password: str


class SUserLogin(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    mail: EmailStr
    password: str


class SRestorePassword(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    mail: EmailStr

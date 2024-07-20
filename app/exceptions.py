from fastapi import HTTPException, status


class PoCException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class UsernameAlreadyExistsException(PoCException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Username уже существует."


class EmailAlreadyExistException(PoCException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Email уже существует."


class IncorrectEmailOrPasswordException(PoCException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверная почта или пароль."


class TokenExpiredException(PoCException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Токен истек."


class TokenAbsentException(PoCException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Токен отсутствует."


class IncorrectTokenFormatException(PoCException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверный формат токена."


class UserIsNotPresentException(PoCException):
    status_code = status.HTTP_401_UNAUTHORIZED


class AccessDeniedException(PoCException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Only admins can perform this action"


class ObjectNotFoundException(PoCException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Object not found"


class ClicksDataException(PoCException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Invalid data"

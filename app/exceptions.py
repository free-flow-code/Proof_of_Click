from fastapi import HTTPException, status


class PoCException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class BadRequestException(PoCException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Incorrect data requested."


class UsernameAlreadyExistsException(PoCException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Username already exists."


class EmailAlreadyExistException(PoCException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Email already exists."


class IncorrectEmailOrPasswordException(PoCException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Incorrect email or password."


class TokenExpiredException(PoCException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Token expired."


class TokenAbsentException(PoCException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Token is missing."


class IncorrectTokenFormatException(PoCException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Invalid token format."


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


class InternalServerError(PoCException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "We apologize. The server is in trouble. Try later"


class IncorrectEmailCodeException(PoCException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Incorrect email code"


class NotEnoughFundsException(PoCException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Not enough funds."  # недостаточно средств

class ValueException(PoCException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Cannot get value"

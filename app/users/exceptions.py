from app.exceptions import AppException


class InvalidToken(AppException):
    pass


class InvalidAccessType(AppException):
    pass

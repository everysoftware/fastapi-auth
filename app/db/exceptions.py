from app.exceptions import AppException


class DbException(AppException):
    pass


class NoSuchEntity(DbException):
    pass

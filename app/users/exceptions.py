from starlette import status

from app.exceptions import BackendError


class UserAlreadyExists(BackendError):
    message = "User with this email already exists"
    error_code = "user_already_exists"
    status_code = status.HTTP_400_BAD_REQUEST


class Unauthorized(BackendError):
    status_code = status.HTTP_401_UNAUTHORIZED
    headers = {"WWW-Authenticate": "Bearer"}


class NoTokenProvided(Unauthorized):
    message = "No access token provided"
    error_code = "no_token_provided"


class UserEmailNotFound(Unauthorized):
    message = "User with this email not found"
    error_code = "user_email_not_found"


class WrongPassword(Unauthorized):
    message = "Wrong password"
    error_code = "wrong_password"


class InvalidToken(Unauthorized):
    message = "Invalid token"
    error_code = "invalid_token"


class InvalidTokenType(Unauthorized):
    error_code = "invalid_token_type"


class NoPermission(BackendError):
    message = "You don't have permission to do this"
    error_code = "no_permission"
    status_code = status.HTTP_403_FORBIDDEN


class UserNotFound(Unauthorized):
    message = "User with this id not found"
    error_code = "user_not_found"


class CodeExpired(BackendError):
    message = "Code expired"
    error_code = "code_expired"
    status_code = status.HTTP_400_BAD_REQUEST


class WrongCode(BackendError):
    message = "Wrong code"
    error_code = "wrong_code"
    status_code = status.HTTP_400_BAD_REQUEST

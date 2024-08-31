from starlette import status

from app.exceptions import BackendError


class UserAlreadyExists(BackendError):
    message = "User with this email already exists"
    error_code = "user_already_exists"
    status_code = status.HTTP_400_BAD_REQUEST


class InvalidGrantType(BackendError):
    message = "Invalid grant type"
    error_code = "invalid_grant_type"
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


class UserNotFound(Unauthorized):
    message = "User with this id not found"
    error_code = "user_not_found"


class SuperuserRightsRequired(BackendError):
    message = "You must be superuser to do this"
    error_code = "superuser_rights_required"
    status_code = status.HTTP_403_FORBIDDEN

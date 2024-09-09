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


class UserNotFound(Unauthorized):
    message = "User with this id not found"
    error_code = "user_not_found"


class SuperuserRightsRequired(BackendError):
    message = "You must be superuser to do this"
    error_code = "not_superuser"
    status_code = status.HTTP_403_FORBIDDEN


class PasswordSettingRequired(BackendError):
    message = "You must set password to do this"
    error_code = "password_not_set"
    status_code = status.HTTP_403_FORBIDDEN


class VerificationRequired(BackendError):
    message = "You must set password to do this"
    error_code = "not_verified"
    status_code = status.HTTP_403_FORBIDDEN


class UserDisabled(BackendError):
    message = "User is disabled"
    error_code = "user_disabled"
    status_code = status.HTTP_403_FORBIDDEN

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


class WrongCode(BackendError):
    message = "Wrong code"
    error_code = "wrong_code"
    status_code = status.HTTP_400_BAD_REQUEST


class SSOAlreadyAssociatedThisUser(BackendError):
    message = "SSO account is already associated with this user"
    error_code = "sso_already_associated"
    status_code = status.HTTP_400_BAD_REQUEST


class SSOAlreadyAssociatedAnotherUser(BackendError):
    message = "SSO account is already associated with another user"
    error_code = "sso_already_associated"
    status_code = status.HTTP_400_BAD_REQUEST


class TelegramNotConnected(BackendError):
    message = "Telegram account is not connected"
    error_code = "telegram_not_connected"
    status_code = status.HTTP_400_BAD_REQUEST


class EmailNotSet(BackendError):
    message = "Email is not set"
    error_code = "email_not_set"
    status_code = status.HTTP_400_BAD_REQUEST

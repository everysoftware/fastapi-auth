from starlette import status

from app.exceptions import BackendError


class NotSupported(NotImplementedError):
    def __init__(self) -> None:
        super().__init__("Provider not supported")


class Unauthorized(RuntimeError):
    def __init__(self) -> None:
        super().__init__(
            "Authorization data not found. Did you forget to call 'login'?"
        )


class SSOError(BackendError):
    pass


class SSOLoginError(SSOError):
    message = "SSO login error"
    error_code = "sso_login_error"
    status_code = status.HTTP_401_UNAUTHORIZED


class SSODisabled(SSOError):
    message = "SSO via this provider is disabled"
    error_code = "sso_disabled"
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE


class InvalidTelegramHash(BackendError):
    message = "Invalid Telegram data hash"
    error_code = "invalid_telegram_hash"
    status_code = status.HTTP_401_UNAUTHORIZED


class TelegramAuthDataExpired(BackendError):
    message = "Telegram auth data expired"
    error_code = "telegram_auth_data_expired"
    status_code = status.HTTP_401_UNAUTHORIZED

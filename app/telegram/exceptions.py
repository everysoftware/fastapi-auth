from starlette import status

from app.exceptions import BackendError


class InvalidTelegramHash(BackendError):
    message = "Invalid Telegram data hash"
    error_code = "invalid_telegram_hash"
    status_code = status.HTTP_401_UNAUTHORIZED


class TelegramAuthDataExpired(BackendError):
    message = "Telegram auth data expired"
    error_code = "telegram_auth_data_expired"
    status_code = status.HTTP_401_UNAUTHORIZED

from starlette import status

from app.exceptions import BackendError


class UnsetStateWarning(UserWarning):
    """Warning about unset state parameter."""


class OIDCError(BackendError):
    pass


class OIDCLoginError(OIDCError):
    error_code = "sso_login_error"
    status_code = status.HTTP_401_UNAUTHORIZED

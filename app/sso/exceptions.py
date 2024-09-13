from starlette import status

from app.exceptions import BackendError


class SSOError(BackendError):
    pass


class SSOLoginError(SSOError):
    error_code = "sso_login_error"
    status_code = status.HTTP_401_UNAUTHORIZED


class SSODisabled(BackendError):
    message = "SSO via this provider is disabled"
    error_code = "sso_disabled"
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE


class UnsetStateWarning(UserWarning):
    pass

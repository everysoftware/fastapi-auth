from starlette import status

from app.exceptions import BackendError


class SSODisabled(BackendError):
    message = "SSO via this provider is disabled"
    error_code = "sso_disabled"
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE

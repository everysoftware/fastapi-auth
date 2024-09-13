from starlette import status

from app.exceptions import BackendError


class SSOAccountNotFound(BackendError):
    message = "SSO account with this id not found"
    error_code = "sso_account_not_found"
    status_code = status.HTTP_404_NOT_FOUND

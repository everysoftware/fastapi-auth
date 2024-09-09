from starlette import status

from app.exceptions import BackendError


class SSODisabled(BackendError):
    message = "SSO via this provider is disabled"
    error_code = "sso_disabled"
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE


class SSOAlreadyAssociatedThisUser(BackendError):
    message = "SSO account is already associated with this user"
    error_code = "sso_already_associated"
    status_code = status.HTTP_400_BAD_REQUEST


class SSOAlreadyAssociatedAnotherUser(BackendError):
    message = "SSO account is already associated with another user"
    error_code = "sso_already_associated"
    status_code = status.HTTP_400_BAD_REQUEST


class SSOAccountNotFound(BackendError):
    message = "SSO account with this id not found"
    error_code = "sso_account_not_found"
    status_code = status.HTTP_404_NOT_FOUND

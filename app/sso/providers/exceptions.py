from starlette import status

from app.exceptions import BackendError


class SSOLoginError(BackendError):
    """Raised when any login-related error occurs.

    Such as when user is not verified or if there was an attempt for fake login.
    """

    error_code = "sso_login_error"
    status_code = status.HTTP_401_UNAUTHORIZED


class UnsetStateWarning(UserWarning):
    """Warning about unset state parameter."""


class ReusedOauthClientWarning(UserWarning):
    """Warning about reused oauth client instance."""

from starlette import status

from app.exceptions import BackendError


class EmailNotificationsDisabled(BackendError):
    message = "Email notifications are disabled"
    error_code = "email_notifications_disabled"
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE

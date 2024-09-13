import warnings
from typing import Any

from starlette.concurrency import run_in_threadpool

from app.config import settings
from app.mail import client
from app.mail.base import MailMessage
from app.service import Service
from app.users.schemas import UserRead


class NotificationService(Service):
    @staticmethod
    async def send_email(
        user: UserRead, subject: str, template: str, **kwargs: Any
    ) -> None:
        if settings.mail.mail_enabled:
            msg = MailMessage(
                subject=subject, template=template, user=user
            ).as_email(**kwargs)
            await run_in_threadpool(client.send_email, msg)
        else:
            warnings.warn(
                "Emails are disabled. Set MAIL_ENABLED=True to enable sending emails.",
                UserWarning,
            )

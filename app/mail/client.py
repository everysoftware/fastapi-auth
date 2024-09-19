import smtplib
from email.message import Message
from typing import Any

from app.config import settings
from app.mail.schemas import MailMessage
from app.users.schemas import UserRead


class MailClient:
    client: smtplib.SMTP_SSL

    def __init__(self) -> None:
        if not settings.mail.mail_enabled:
            return
        self.client = smtplib.SMTP_SSL(
            settings.mail.smtp_host, settings.mail.smtp_port
        )
        self.client.login(
            settings.mail.smtp_username, settings.mail.smtp_password
        )

    def send_msg(self, message: Message) -> None:
        with self.client as session:
            session.send_message(message)

    def send(
        self, user: UserRead, subject: str, template: str, **kwargs: Any
    ) -> None:
        msg = MailMessage(
            subject=subject, template=template, user=user
        ).as_email(**kwargs)
        return self.send_msg(msg)

from email.message import Message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from jinja2 import Environment, FileSystemLoader

from app.config import settings
from app.schemas import BackendBase
from app.users.schemas import UserRead

env = Environment(loader=FileSystemLoader("templates/mail"))


class MailMessage(BackendBase):
    subject: str
    template: str
    user: UserRead

    def as_email(self, **kwargs: Any) -> Message:
        html = env.get_template(f"{self.template}.html").render(
            user=self.user, **kwargs
        )

        msg = MIMEMultipart("alternative")
        msg["From"] = settings.mail.smtp_from_name
        msg["To"] = self.user.email
        msg["Subject"] = self.subject

        msg.attach(MIMEText(html, "html"))
        return msg

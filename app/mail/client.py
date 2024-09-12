import smtplib
from email.message import Message

from app.config import settings


def smtp_session() -> smtplib.SMTP_SSL:
    client = smtplib.SMTP_SSL(settings.mail.smtp_host, settings.mail.smtp_port)
    client.login(settings.mail.smtp_username, settings.mail.smtp_password)
    return client


def send_email(message: Message) -> None:
    with smtp_session() as session:
        session.send_message(message)

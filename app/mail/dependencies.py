from typing import Annotated

from fastapi import Depends

from app.mail.client import MailClient


def get_mail() -> MailClient:
    return MailClient()


MailDep = Annotated[MailClient, Depends(get_mail)]

from typing import Annotated

from fastapi import Depends

from app.notifications.service import NotificationService

NotificationServiceDep = Annotated[NotificationService, Depends()]

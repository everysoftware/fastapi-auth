# Import models for alembic

from app.users.models import UserOrm
from .base import BaseOrm

__all__ = ["BaseOrm", "UserOrm"]

from fastapi import FastAPI
from sqladmin import Admin

from app.admin.auth import auth_backend
from app.admin.views import SSOAccountAdmin, UserAdmin
from app.db.connection import async_engine

app = FastAPI()
admin = Admin(app, async_engine, authentication_backend=auth_backend)

admin.add_view(UserAdmin)
admin.add_view(SSOAccountAdmin)

from fastapi.templating import Jinja2Templates

from app.config import settings

templates = Jinja2Templates(directory="templates/pages")
templates.env.globals["app_display_name"] = settings.app_display_name

from app.schemas import BackendSettings


class DBSettings(BackendSettings):
    db_url: str = "postgresql+asyncpg://postgres:changethis@db:5432/app"
    db_echo: bool = False

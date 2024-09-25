from app.schemas import BackendSettings


class CacheSettings(BackendSettings):
    redis_key: str = "fastapi"
    redis_url: str = "redis://default+changethis@localhost:6379/0"

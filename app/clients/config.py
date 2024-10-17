from app.schemas import BackendSettings


class ClientSettings(BackendSettings):
    client_name: str = "Frontend"
    client_id: str = "frontend"
    client_secret: str = "changethis"
    client_urls: list[str] = "https://localhost:3000"

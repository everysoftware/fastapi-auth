from app.schemas import BackendSettings


class ObservabilitySettings(BackendSettings):
    tempo_url: str = "http://host.docker.internal:4317"

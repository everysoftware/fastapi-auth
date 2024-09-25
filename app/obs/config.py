from app.schemas import BackendSettings


class ObservabilitySettings(BackendSettings):
    export_url: str = "http://tempo:4317"

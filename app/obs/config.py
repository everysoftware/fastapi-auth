from app.schemas import BackendSettings


class ObservabilitySettings(BackendSettings):
    otlp_grpc_url: str = "http://tempo:4317"

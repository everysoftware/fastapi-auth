from fastapi import FastAPI
from fastapi import Request, Response
from prometheus_client import REGISTRY
from prometheus_client.openmetrics.exposition import (
    generate_latest,
    CONTENT_TYPE_LATEST,
)

from app.config import settings
from app.obs.metrics import setting_otlp, PrometheusMiddleware


def get_metrics(request: Request) -> Response:  # noqa
    return Response(
        generate_latest(REGISTRY),  # type: ignore[no-untyped-call]
        headers={"Content-Type": CONTENT_TYPE_LATEST},
    )


def setup_obs(app: FastAPI) -> None:
    app.add_middleware(PrometheusMiddleware, app_name=settings.app_name)  # noqa
    app.add_route("/metrics", get_metrics)
    setting_otlp(app, settings.app_name, settings.obs.otlp_grpc_url)

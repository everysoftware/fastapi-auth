import logging

from fastapi import FastAPI

from app.config import settings
from app.db.connection import async_engine
from app.obs.logging import EndpointFilter
from app.obs.metrics import PrometheusMiddleware, get_metrics
from app.obs.tracing import instrument


def setup_logging() -> None:
    logger = logging.getLogger("uvicorn.access")
    logger.addFilter(EndpointFilter())


def setup_metrics(app: FastAPI) -> None:
    app.add_middleware(PrometheusMiddleware, app_name=settings.app_name)  # noqa
    app.add_route("/metrics", get_metrics)
    instrument(
        app,
        async_engine,
        export_url=settings.obs.export_url,
        app_name=settings.app_name,
    )


def setup_obs(app: FastAPI) -> None:
    setup_logging()
    setup_metrics(app)


main_log = logging.getLogger("fastapiapp")

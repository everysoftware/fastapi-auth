import time

from fastapi import Request, Response
from fastapi import status
from opentelemetry import trace
from prometheus_client import REGISTRY
from prometheus_client.openmetrics.exposition import (
    generate_latest,
    CONTENT_TYPE_LATEST,
)
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.routing import Match
from starlette.types import ASGIApp

from app.exc_handlers import unhandled_exception_handler
from app.obs import panels


class PrometheusMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, *, app_name: str = "fastapiapp") -> None:
        super().__init__(app)
        self.app_name = app_name
        panels.INFO.labels(app_name=self.app_name).inc()

    @staticmethod
    def get_path(request: Request) -> tuple[str, bool]:
        """Get path from request and check if it is defined in the app routes."""
        for route in request.app.routes:
            match, _ = route.matches(request.scope)
            if match == Match.FULL:
                return route.path, True
        return request.url.path, False

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        method = request.method
        path, is_defined = self.get_path(request)

        if not is_defined:
            return await call_next(request)

        panels.REQUESTS_IN_PROGRESS.labels(
            method=method, path=path, app_name=self.app_name
        ).inc()
        panels.REQUESTS.labels(
            method=method, path=path, app_name=self.app_name
        ).inc()
        before_time = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception as e:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            panels.EXCEPTIONS.labels(
                method=method,
                path=path,
                exception_type=type(e).__name__,
                app_name=self.app_name,
            ).inc()
            return unhandled_exception_handler(request, e)
        else:
            status_code = response.status_code
            after_time = time.perf_counter()
            # Retrieve trace id for exemplar
            span = trace.get_current_span()
            trace_id = trace.format_trace_id(span.get_span_context().trace_id)
            panels.REQUESTS_PROCESSING_TIME.labels(
                method=method, path=path, app_name=self.app_name
            ).observe(after_time - before_time, exemplar={"TraceID": trace_id})
        finally:
            panels.RESPONSES.labels(
                method=method,
                path=path,
                status_code=status_code,  # noqa
                app_name=self.app_name,
            ).inc()
            panels.REQUESTS_IN_PROGRESS.labels(
                method=method, path=path, app_name=self.app_name
            ).dec()

        return response


def get_metrics(request: Request) -> Response:  # noqa
    return Response(
        generate_latest(REGISTRY),  # type: ignore[no-untyped-call]
        headers={"Content-Type": CONTENT_TYPE_LATEST},
    )

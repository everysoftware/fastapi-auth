from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings


def setup_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,  # noqa
        allow_origins=settings.cors.cors_origins,
        allow_origin_regex=settings.cors.cors_origin_regex,
        allow_credentials=True,
        allow_methods=settings.cors.cors_methods,
        allow_headers=settings.cors.cors_headers,
    )

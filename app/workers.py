from uvicorn_worker import UvicornWorker


class MyUvicornWorker(UvicornWorker):  # type: ignore[misc]
    CONFIG_KWARGS = {
        "log_config": "logging.yaml",
    }

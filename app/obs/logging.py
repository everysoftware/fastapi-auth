import logging
import sys

logging_handler = logging.StreamHandler(sys.stdout)


def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    logger: logging.Logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger


main_log = get_logger("main")


class EndpointFilter(logging.Filter):
    # Uvicorn endpoint access log filter
    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find("GET /metrics") == -1


# Filter out /endpoint
logging.getLogger("uvicorn.access").addFilter(EndpointFilter())

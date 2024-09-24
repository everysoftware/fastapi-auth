import logging


# Setting up the access logger
class EndpointFilter(logging.Filter):
    # Uvicorn endpoint access log filter
    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find("GET /metrics") == -1


logger = logging.getLogger("uvicorn.access")
logger.addFilter(EndpointFilter())

main_log = logging.getLogger("fastapiapp")
main_log.setLevel(logging.INFO)
if not (default_handler := logging.getHandlerByName("default")):
    raise RuntimeError("Incorrect log config: no default handler")
main_log.addHandler(default_handler)
main_log.propagate = False

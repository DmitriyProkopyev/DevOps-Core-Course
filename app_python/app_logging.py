import logging
import logging.config
import sys

from fastapi import Request, Response
from pythonjsonlogger.json import JsonFormatter

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.json.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "json",
        }
    },
    "root": {
        "level": "NOTSET",
        "handlers": ["console"],
    },
}

logging.config.dictConfig(LOGGING)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s"))

app_logger = logging.getLogger("root")
app_logger.addHandler(handler)
app_logger.propagate = False

request_logger = logging.getLogger("app.request")
request_logger.setLevel(level=logging.INFO)
request_logger.propagate = True

error_logger = logging.getLogger("app.error")
error_logger.setLevel(level=logging.ERROR)
error_logger.propagate = True


def log_error(request: Request):
    error_logger.error(
        "Unhandled exception occured in a request",
        extra={
            "app": "devops-info-service",
            "logging": "promtail",
            "path": request.url.path,
            "method": request.method
        },
        exc_info=True)


def log_request(request: Request, response: Response, execution_time: float):
    request_logger.info(
        "New request was processed",
        extra={
            "app": "devops-info-service",
            "logging": "promtail",
            "path": request.url.path,
            "method": request.method,
            "execution_time": execution_time,
            "status_code": response.status_code
        })

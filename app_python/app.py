import logging
import os
import sys

from app_stats import AppStats
from datetime import datetime, timezone
from pythonjsonlogger import json
from typing import Any

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse


app = FastAPI()
app_logger = logging.getLogger("app")

major_version = int(os.environ.get("MAJOR_VERSION", 1))
minor_version = int(os.environ.get("MINOR_VERSION", 0))
patch_version = int(os.environ.get("PATCH_VERSION", 0))

if not app_logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = json.JsonFormatter(reserved_attrs=[], timestamp=True)
    handler.setFormatter(formatter)
    app_logger.addHandler(handler)

request_logger = logging.getLogger("app.request")
error_logger = logging.getLogger("app.error")

request_logger.setLevel(level=logging.INFO)
error_logger.setLevel(level=logging.ERROR)

app_stats = AppStats(name="devops-info-service",
                     description="DevOps course info service",
                     major_version=major_version,
                     minor_version=minor_version,
                     patch_version=patch_version)


@app.get("/", description="Service information")
async def root(request: Request):
    request_info = {
        "client_ip": request.client.host,
        "user_agent": request.headers.get('user-agent'),
        "method": request.method,
        "path": request.url.path
    }

    endpoints_info = list()
    for _, key in enumerate(endpoint_paths):
        path = key
        method = next(iter(endpoint_paths[key]))
        description = endpoint_paths[key][method]['description']
        endpoints_info.append({"path": path, "method": method.upper(), "description": description})

    return {
        "service": app_stats.provide_service_info(),
        "system": app_stats.provide_system_info(),
        "runtime": app_stats.provide_runtime_info(),
        "request": request_info,
        "endpoints": endpoints_info
    }

@app.get("/health", description="Health check")
async def check_health():
    return {
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'uptime_seconds': int(app_stats.get_uptime())
    }

@app.exception_handler(Exception)
async def handle_general_exception(request: Request, exception: Exception):
    error_logger.error(
        "Unhandled exception occured in a request",
        extra={
            "path": request.url.path,
            "method": request.method
        },
        exc_info=True)

    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error"}
    )

@app.middleware("http")
async def log_request(request: Request, call_next):
    call_time = datetime.now(timezone.utc)
    response: Response = await call_next(request)
    execution_time = datetime.now(timezone.utc) - call_time
    request_logger.info(
        "New request was processed",
        extra={
            "path": request.url.path,
            "method": request.method,
            "execution_time": execution_time,
            "status_code": response.status_code
        })
    return response


endpoint_paths: dict[str, Any] = app.openapi()['paths']

if __name__ == "__main__":
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    logging.getLogger("uvicorn").disabled = True
    logging.getLogger("uvicorn.access").disabled = True
    uvicorn.run(app, host=HOST, port=PORT, log_config=None)

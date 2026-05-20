import os
import uvicorn

from app_stats import AppStats
from observability import Observer
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse


VISITS_PATH = Path("/data/visits.txt")
VISITS_PATH.parent.mkdir(parents=True, exist_ok=True)


app = FastAPI()
major_version = int(os.environ.get("MAJOR_VERSION", 1))
minor_version = int(os.environ.get("MINOR_VERSION", 0))
patch_version = int(os.environ.get("PATCH_VERSION", 0))
app_stats = AppStats(name="devops-info-service",
                     description="DevOps course info service",
                     major_version=major_version,
                     minor_version=minor_version,
                     patch_version=patch_version)
observer = Observer(app_stats)


def read_visits():
    try:
        return int(VISITS_PATH.read_text().strip())
    except (FileNotFoundError, ValueError):
        return 0


def increment_visits():
    value = read_visits() + 1
    VISITS_PATH.write_text(f"{value}\n")


@app.get("/", description="Service information")
async def root(request: Request):
    increment_visits()

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


@app.get("/trigger_error", description="Debugging endpoint to trigger intentional errors")
async def trigger_error():
    raise Exception("You triggered an intentional error!")


@app.get("/metrics", description="Prometheus metrics endpoint for standard and custom observability")
async def metrics():
    return observer.snapshot_current_metrics()


@app.get("/visits", description="An endpoint that returns the number of root endpoint calls")
async def visits():
    return {
        "visits": read_visits()
    }


@app.exception_handler(Exception)
async def handle_general_exception(request: Request, exception: Exception):
    observer.record_error(request)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error"}
    )


@app.middleware("http")
async def log_request_middleware(request: Request, call_next):
    observer.record_request_start(request.url.path)
    call_time = datetime.now(timezone.utc)
    response: Response = await call_next(request)
    execution_time = (datetime.now(timezone.utc) - call_time).total_seconds()
    observer.record_request(request, response, execution_time)
    observer.record_request_end(request.url.path)
    return response


endpoint_paths: dict[str, Any] = app.openapi()['paths']

if __name__ == "__main__":
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    logging.getLogger("uvicorn").disabled = True
    logging.getLogger("uvicorn.access").disabled = True
    uvicorn.run(app, host=HOST, port=PORT, log_config=None)

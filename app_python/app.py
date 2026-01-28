import logging
import os
import platform
import socket
import sys
from datetime import datetime, timezone
from pythonjsonlogger import jsonlogger
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

app = FastAPI()
app_logger = logging.getLogger("app")

if not app_logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(reserved_attrs=[], timestamp=True)
    handler.setFormatter(formatter)
    app_logger.addHandler(handler)

request_logger = logging.getLogger("app.request")
error_logger = logging.getLogger("app.error")

request_logger.setLevel(level=logging.INFO)
error_logger.setLevel(level=logging.ERROR)


class AppStats:
    def __init__(self, name: str, description: str, major_version: int, minor_version: int, patch_version: int):
        if len(name) == 0 or name is None:
            raise ValueError("The service name must not be empty!")
        
        if len(description) == 0 or description is None:
            raise ValueError("The service description must not be empty!")
        
        if major_version < 0 or minor_version < 0 or patch_version < 0:
            raise ValueError("The service version must be non negative!")
        
        self.start_time = datetime.now(timezone.utc)
        self.name = name
        self.description = description
        self.version = f"{major_version}.{minor_version}.{patch_version}"
        self.framework = "FastAPI"

    def provide_service_info(self) -> Dict[str, Any]: 
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "framework": self.framework
        }
    
    def provide_system_info(self) -> Dict[str, Any]:
        return {
            "hostname": socket.gethostname(),
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "cpu_count": os.cpu_count(),
            "python_version": platform.python_version()
        }
    
    def get_uptime(self) -> float:
        delta = datetime.now(timezone.utc) - self.start_time
        return delta.total_seconds()
    
    def provide_runtime_info(self) -> Dict[str, str]:
        uptime_seconds = int(self.get_uptime())
        uptime_minutes = (uptime_seconds // 60) % 60
        uptime_hours = uptime_seconds // 3600

        if uptime_hours > 1 or uptime_hours == 0:
            hours_adapted_wording = "hours"
        else:
            hours_adapted_wording = "hour"

        if uptime_minutes > 1 or uptime_minutes == 0:
            minutes_adapted_wording = "minutes"
        else:
            minutes_adapted_wording = "minute"

        return {
            "uptime_seconds": uptime_seconds,
            "uptime_human": f"{uptime_hours} {hours_adapted_wording}, {uptime_minutes} {minutes_adapted_wording}",
            "current_time": datetime.now(timezone.utc).isoformat(),
            "timezone": "UTC"
        }


app_stats = AppStats(name="devops-info-service",
                     description="DevOps course info service",
                     major_version=1,
                     minor_version=0,
                     patch_version=0)

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

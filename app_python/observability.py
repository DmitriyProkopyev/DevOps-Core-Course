import logging
import logging.config
import random
import sys
import time
import math

from app_stats import AppStats
from datetime import datetime
from fastapi import Request, Response
from pythonjsonlogger.json import JsonFormatter

from prometheus_client import Counter, Gauge, Histogram, start_http_server
from prometheus_client import REGISTRY, CONTENT_TYPE_LATEST, generate_latest


REQUESTS_TOTAL = Counter(
    "app_requests_total",
    "Total number of requests",
    ["method", "endpoint", "status"]
)
ERRORS_TOTAL = Counter(
    "app_errors_total",
    "Total number of errors",
    ["method", "endpoint"]
)

INPROGRESS_REQUESTS = Gauge(
    "app_inprogress_requests",
    "Number of in-progress requests",
    ["endpoint"]
)
LAST_REQUEST_TIME = Gauge(
    "app_last_request_time",
    "Elapsed seconds since app start when the last request was made",
    ["endpoint"]
)

REQUEST_EXECUTION_TIME= Histogram(
    "app_request_latency_seconds",
    "Request latency in seconds",
    ["method", "endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
)
REQUESTS_PER_UPTIME_DENSITY = Histogram(
    "app_request_density_over_uptime",
    "Request density in seconds over uptime",
    ["endpoint"],
    buckets=(0, 1, 2, 3, 5, 7, 10)
)


handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s"))

app_logger = logging.getLogger("app")
app_logger.addHandler(handler)
app_logger.propagate = False

request_logger = logging.getLogger("app.request")
request_logger.setLevel(level=logging.INFO)
request_logger.propagate = False

error_logger = logging.getLogger("app.error")
error_logger.setLevel(level=logging.ERROR)
error_logger.propagate = False


class Observer:
    def __init__(self, app_stats: AppStats):
        self.app_stats = app_stats
        self.density_bucket_size = 30
        self.density_buckets_groups = {
            "/": list(),
            "/health": list(),
            "/trigger_error": list(),
            "/metrics": list()
        }

    def record_error(self, request: Request):
        error_logger.error(
            "Unhandled exception occured in a request",
            extra={
                "app": "devops-info-service",
                "logging": "promtail",
                "path": request.url.path,
                "method": request.method
            },
            exc_info=True)

        uptime_seconds = self.app_stats.get_uptime()
        REQUESTS_TOTAL.labels(method=request.method, endpoint=request.url.path, status="500").inc()
        LAST_REQUEST_TIME.labels(endpoint=request.url.path).set(uptime_seconds)
        ERRORS_TOTAL.labels(method=request.method, endpoint=request.url.path).inc()

    def record_request(self, request: Request, response: Response, execution_time: float):
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

        uptime_seconds = self.app_stats.get_uptime()
        REQUESTS_TOTAL.labels(method=request.method, endpoint=request.url.path, status=str(response.status_code)).inc()
        LAST_REQUEST_TIME.labels(endpoint=request.url.path).set(uptime_seconds)
        REQUEST_EXECUTION_TIME.labels(method=request.method, endpoint=request.url.path).observe(execution_time)

        density_buckets = self.density_buckets_groups[request.url.path]
        bucket_index = int(math.floor(uptime_seconds)) // 30
        if len(density_buckets) <= bucket_index:
            for _ in range(bucket_index - len(density_buckets) + 1):
                REQUESTS_PER_UPTIME_DENSITY.labels(endpoint=request.url.path).observe(0)
                density_buckets.append(0)

        if bucket_index > 0 and density_buckets[bucket_index] == 0:
            REQUESTS_PER_UPTIME_DENSITY.labels(endpoint=request.url.path).observe(density_buckets[bucket_index - 1])

        density_buckets[bucket_index] += 1

 
    def record_request_start(self, endpoint: str):
        INPROGRESS_REQUESTS.labels(endpoint=endpoint).inc()

    def record_request_end(self, endpoint: str):
        INPROGRESS_REQUESTS.labels(endpoint=endpoint).dec()

    def snapshot_current_metrics(self):
        data = generate_latest(REGISTRY)
        return Response(content=data, media_type=CONTENT_TYPE_LATEST)

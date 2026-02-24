import pytest
import re

from app import app
from fastapi.testclient import TestClient
from utils.json_auditor import JSONAuditor


ROOT_PATH = "/"
HEALTH_PATH = "/health"
NAME_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9\s_./,-]*[A-Za-z0-9]$"
ISO_DATETIME_PATTERN = r"^\d{4}-[01]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\d(\.\d+)?([+-][0-2]\d:[0-5]\d|Z)?$"

EXPECTED_ROOT_STRUCTURE = {
    "service": {
        "name": NAME_PATTERN,
        "version": r"^\d+.\d+.\d+$",
        "description": NAME_PATTERN,
        "framework": r"^FastAPI$",
    },
    "system": {
        "hostname": NAME_PATTERN,
        "platform": NAME_PATTERN,
        "platform_version": r"^.+$",
        "architecture": NAME_PATTERN,
        "cpu_count": r"^\d+$",
        "python_version": r"^\d+.\d+.\d+$",
    },
    "runtime": {
        "uptime_seconds": r"^\d+$",
        "uptime_human": r"^\d+(?:\s+(?:hour|hours), \d+(?:\s+(?:minute|minutes)))$",
        "current_time": ISO_DATETIME_PATTERN,
        "timezone": r"^UTC$",
    },
    "request": {
        "client_ip": r"^(?:\d+.\d+.\d+.\d+|testclient)$",
        "user_agent": NAME_PATTERN,
        "method": r"^(?:GET|HEAD|POST|PATCH|PUT|UPDATE|DELETE|OPTIONS|TRACE)$",
        "path": r"^/[a-zA-Z0-9_%-]*(?:/[a-zA-Z0-9_%-]+)*/?$",
    },
    "endpoints": [
        {"path": r"^/$", "method": r"^GET$", "description": NAME_PATTERN},
        {"path": r"^/health$", "method": r"^GET$", "description": NAME_PATTERN},
    ],
}
EXPECTED_HEALTH_STRUCTURE = {
    'status': 'healthy',
    'timestamp': ISO_DATETIME_PATTERN,
    'uptime_seconds': r"^\d+$"
}


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_root(client: TestClient):
    auditor = JSONAuditor(EXPECTED_ROOT_STRUCTURE)
    response = client.get(ROOT_PATH)
    assert response.status_code == 200

    data = response.json()

    for (expected, actual) in auditor.as_pairs(data):
        assert re.match(pattern=str(expected), string=str(actual)) is not None


def test_health(client: TestClient):
    auditor = JSONAuditor(EXPECTED_HEALTH_STRUCTURE)
    response = client.get(HEALTH_PATH)
    assert response.status_code == 200

    data = response.json()

    for (expected, actual) in auditor.as_pairs(data):
        assert re.match(pattern=str(expected), string=str(actual)) is not None

import pytest
import random
import time

from app_stats import AppStats


def test_init_integrity_break():
    with pytest.raises(ValueError) as exception_info:
        AppStats("", "description", 1, 1, 1)
    
    assert "name" in str(exception_info)

    with pytest.raises(ValueError) as exception_info:
        AppStats("name", "", 1, 1, 1)

    assert "description" in str(exception_info)

    with pytest.raises(ValueError) as exception_info:
        AppStats("name", "description", -1, 1, 1)

    assert "version" in str(exception_info)

    with pytest.raises(ValueError) as exception_info:
        AppStats("name", "description", 1, -1, 1)

    assert "version" in str(exception_info)

    with pytest.raises(ValueError) as exception_info:
        AppStats("name", "description", 1, 1, -1)

    assert "version" in str(exception_info)


def test_service_info():
    name = "test name"
    description = "test description"

    reproducibility_seed = random.random()
    random.seed(reproducibility_seed)
    print("Seed for reproducibility: ", reproducibility_seed)

    for i in range(20):
        major_version = random.randint(0, 999)
        minor_version = random.randint(0, 999)
        patch_version = random.randint(0, 999)
        version = f"{major_version}.{minor_version}.{patch_version}"
        
        app_stats = AppStats(name, description, major_version, minor_version, patch_version)

        expected_structure = {
            "name": name,
            "version": version,
            "description": description,
            "framework": "FastAPI"
        }

        assert expected_structure == app_stats.provide_service_info()

    app_stats = AppStats("name", "description", 1, 0, 0)
    

def test_system_info_consistency():
    app_stats = AppStats("name", "description", 1, 0, 0)
    expected_keys = ["hostname", "platform", "platform_version", "architecture", "cpu_count", "python_version"]

    first_capture = app_stats.provide_system_info()
    time.sleep(5)
    second_capture = app_stats.provide_system_info()

    for key in expected_keys:
        assert first_capture[key] == second_capture[key]


def test_runtime_info_progression():
    app_stats = AppStats("name", "description", 1, 0, 0)
    dynamic_keys = ["uptime_seconds", "current_time"]

    delay = 5
    epsilon = 0.1

    first_capture = app_stats.provide_runtime_info()
    time.sleep(delay)
    second_capture = app_stats.provide_runtime_info()

    for key in dynamic_keys:
        assert first_capture[key] != second_capture[key]

    assert second_capture["uptime_seconds"] - first_capture["uptime_seconds"] <= delay + epsilon

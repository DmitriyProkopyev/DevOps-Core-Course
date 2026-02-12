import pytest
import random

from app_stats import AppStats


def test_init_integrity_break():
    with pytest.raises(ValueError) as exception_info:
        app_stats = AppStats("", "description", 1, 1, 1)
    
    assert "name" in str(exception_info)

    with pytest.raises(ValueError) as exception_info:
        app_stats = AppStats("name", "", 1, 1, 1)

    assert "description" in str(exception_info)

    with pytest.raises(ValueError) as exception_info:
        app_stats = AppStats("name", "description", -1, 1, 1)

    assert "version" in str(exception_info)

    with pytest.raises(ValueError) as exception_info:
        app_stats = AppStats("name", "description", 1, -1, 1)

    assert "version" in str(exception_info)

    with pytest.raises(ValueError) as exception_info:
        app_stats = AppStats("name", "description", 1, 1, -1)

    assert "version" in str(exception_info)

    name = "test name"
    description = "test description"

    reproducibility_seed = random.random()
    random.seed(reproducibility_seed)
    print("Seed for reproducibility: ", reproducibility_seed)

    for i in range(100):
        major_version = random.random(0, 999)
        minor_version = random.random(0, 999)
        patch_version = random.random(0, 999)
        version
        
        app_stats = AppStats(name, description, major_version, minor_version, patch_version)
        assert (app_stats.name, app_stats.description)


def test_service_info():
    app_stats = AppStats("name", "description", 1, 0, 0)


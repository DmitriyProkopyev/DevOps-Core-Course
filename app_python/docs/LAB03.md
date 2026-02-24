### Testing Framework Choice

Given `unittest` and `pytest` as two primary options, I focused my attention on the features that hold most relevance for this project: test discovery, setup/teardown (fixture) mechanisms, and depth of introspective into failed assert statements. All these features have best coverage in `pytest`, thus that is my choice.


### Test Structure

The tests cover AppStats, the primarily used class of the app, and service endpoints to ensure adequate API outputs. As such, the implemented tests are:

```
tests/
    test_app_stats.py
        test_init_integrity_break()
        test_service_info()
        test_system_info_consistency()
        test_runtime_info_progression()
    test_endpoints.py
        test_root(client: TestClient)
        test_health(client: TestClient)
```


### Running Tests Locally

To run the tests, first navigate to the project root and install the necessary toolset:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
cd app_python
uv sync --dev --locked --no-install-project
```

Then,  and launch pytest on the entire test set:
```bash
uv run pytest tests/
```


### Proof of Validity

Below is a screenshot of all tests passing locally:

![All tests pass](screenshots/all_tests_pass.png)


### Dependency Caching

To assess the build time speedup provided by caching dependencies, I used:

```bash
time docker build \
  --build-arg MAJOR_VERSION=1 \
  --build-arg MINOR_VERSION=0 \
  --build-arg PATCH_VERSION=2 \
  -t devops-info-service:test app_python
```

The result are as following:

| Scenario | Real Time | User Time | System Time | Speedup   |
| -------- | --------- | --------- | ----------- | --------- |
| No Cache | 14.955s   | 0.247s    | 0.531s      | Baseline  |
| Cached   | 2.991s    | 0.176s    | 0.265s      | 5x faster |

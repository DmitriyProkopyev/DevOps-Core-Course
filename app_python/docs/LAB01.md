# Lab 1 Report

## Framework Selection

| Framework | Characteristics                   |
| --------- | --------------------------------- |
| Flask     | Lightweight, easy to learn        |
| FastAPI   | Modern, async, auto-documentation |
| Django    | Full-featured, includes ORM       |

**FastAPI** was chosen for its fitness for modern best practices and auto-documentation, making it suitable for maitaining a production-ready service continuously throughout various changes.


## Best Practices Applied

### Clean code organization

> **Why is it important?**

It keeps the app maintainable in team environments during the entire app lifecycle.

```python
class AppStats:
    def provide_service_info(self) -> Dict[str, Any]...
    
    def provide_system_info(self) -> Dict[str, Any]...
    
    def get_uptime(self) -> float...
    
    def provide_runtime_info(self) -> Dict[str, str]...

async def check_health()...

async def handle_general_exception(request: Request, exception: Exception)...

async def log_request(request: Request, call_next)...
```

All the functions are clear, named after verbs, and grouped logically. Code is organized according to PEP8.

### Universal Error Handling

> **Why is it important?**
> Protects the app from crashing, conceals implementation details

```python
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
```

This setup ensures that any unhandled exceptions are explicitly logged, yet the implementation details are concealed from the clients to eliminate leaks.

### Logging

> **Why is it important?**
> Enables traceability, debugging, and compliance.

```python
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
```

This setup ensures that every request and relevant metadata are always logged.

## API Documentation

### Request/Response Examples

**Example request**: `curl -X 'GET' 'http://127.0.0.1:5000/' -H 'accept: application/json'`

**Response**:
```json
{
  "service": {
    "name": "devops-info-service",
    "version": "1.0.0",
    "description": "DevOps course info service",
    "framework": "FastAPI"
  },
  "system": {
    "hostname": "Master-mind",
    "platform": "Windows",
    "platform_version": "10.0.26100",
    "architecture": "AMD64",
    "cpu_count": 16,
    "python_version": "3.12.10"
  },
  "runtime": {
    "uptime_seconds": 17,
    "uptime_human": "0 hours, 0 minutes",
    "current_time": "2026-01-27T15:54:17.408310+00:00",
    "timezone": "UTC"
  },
  "request": {
    "client_ip": "127.0.0.1",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "method": "GET",
    "path": "/"
  },
  "endpoints": [
    {
      "path": "/",
      "method": "GET",
      "description": "Service information"
    },
    {
      "path": "/health",
      "method": "GET",
      "description": "Health check"
    }
  ]
}
```

**Example request**: `curl -X 'GET' 'http://127.0.0.1:5000/health' -H 'accept: application/json'`

```json
{
  "status": "healthy",
  "timestamp": "2026-01-27T15:57:59.234197+00:00",
  "uptime_seconds": 239
}
```

### Challenges & Solutions

**Problems encountered**:

- Universal logging required request middleware and proper separation of loggers in accordance to FastAPI best practices
    - Solved: created a custom middleware, injected logs into request logger for common logs and into error logger for exception logs
- Universal error handling required its own middleware alongside detail concealment from client for security vs. detail exposure in logs for maintainability
    - Solved: all exceptions are handled in a custom middleware that first logs the details and then returns a plain response

## GitHub Community

> Why does starring repositories matter in open source?

Starring repositories clearly indicates the projects' popularity and community trust, making it easier to discover high-value projects.

> How does following developers helps in team projects and professional growth?

Following developers helps to stay updated on colleagues' work, which facilitates learning across community.

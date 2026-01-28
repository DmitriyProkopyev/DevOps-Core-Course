## Overview

This service provides realtime application, system, and networking data relevant for training in DevOps practices. The data includes app specifics, OS specifics, runtime stats, request data, and available endpoints listing.

## Prerequisites

Python `3.12.x+`, FastAPI `0.120.3+`, uvicorn `0.32.0+`, pythonjsonlogger `4.0.0+`.

## Installation

```py
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the Application

Run with default parameters (`HOST=0.0.0.0`, `PORT=5000`):
```bash
python app.py
```

Or with custom config:

```bash
HOST=<your-value> PORT=<your-value> DEBUG=True python app.py
```

## API Endpoints

- GET / - Service and system information
- GET /health - Health check

**Configuration:**

| Environment Variable | Effect                                                                                  | Default Value |
| -------------------- | --------------------------------------------------------------------------------------- | ------------- |
| HOST                 | Specifies the host for uvicorn                                                          | `0.0.0.0`     |
| PORT                 | Specified the launch port for uvicorn                                                   | `5000`        |
| DEBUG                | Specifies whether to include debug information into responses (currently has no effect) | `False`       |

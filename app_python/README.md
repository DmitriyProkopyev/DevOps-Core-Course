## Overview

This service provides realtime application, system, and networking data relevant for training in DevOps practices. The data includes app specifics, OS specifics, runtime stats, request data, and available endpoints listing.

## Prerequisites

Python `3.12.x+`.

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


## Docker

This section provides command patterns for using the application in a containerized manner.


To build the image locally, execute this command with substitued values:

```bash
docker build -t <name>:<x>.<y>.<z> 
```

To run a container, execute this command with substitued values:

```bash
docker run -d -p <external-port>:5000 <name>:<x>.<y>.<z> 
```

To pull the specific version of the image from DockerHub, execute this command with substitued values:

```bash
docker pull controlw/devops-info-service:<x>.<y>.<z> 
```

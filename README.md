# withoutbg-api

FastAPI-based REST API for AI-powered image background removal — a lightweight wrapper around withoutBG services.
Use it as a self-hosted microservice.

Docker-first • Token auth • FastAPI

## Features

* Background removal endpoint(s)
* Token-based API authentication
* Docker-ready for easy deployment
* FastAPI + Uvicorn stack
* Suitable for microservice architectures

## Repository Structure

```
.
├── app/             # Source code (FastAPI app)
├── Dockerfile       # Docker image definition
├── .github/         # CI / workflows
├── pyproject.toml   # Project config
├── uv.lock
└── README.md
```

## Running with Docker

### Build the Docker image

```
docker build -t withoutbg-api .
```

Or pull the prebuilt image:

```
docker pull ghcr.io/sidharthmenon/withoutbg-api:latest
```

### Configure environment variables

Create a `.env` file in the project root:

```
PORT=8000
PYTHONUNBUFFERED=1
API_TOKENS=token1,token2
```

Environment variables:

```
PORT              Port the API runs on
API_TOKENS        Comma-separated list of valid API tokens
PYTHONUNBUFFERED  Ensures real-time logs in Docker
```

### Run the container

```
docker run \
  --env-file .env \
  -p 8000:8000 \
  --name withoutbg-api \
  ghcr.io/sidharthmenon/withoutbg-api:latest
```

The API will be available at:

```
http://localhost:8000
```

## Docker Compose Setup

Create a `docker-compose.yml` file:

```
version: "3.9"
services:
  withoutbg-api:
    image: ghcr.io/sidharthmenon/withoutbg-api:latest
    container_name: withoutbg-api
    restart: always
    ports:
      - "${PORT}:8000"
    environment:
      PORT: "${PORT}"
      PYTHONUNBUFFERED: "${PYTHONUNBUFFERED}"
      API_TOKENS: "${API_TOKENS}"
```

Start the service:

```
docker compose up -d
```

## Authentication & API Tokens

This API uses token-based authentication.

1. Define one or more tokens in the `API_TOKENS` environment variable (comma-separated).
2. Clients must pass a token on every request (commonly via the Authorization header).
3. Multiple tokens allow easy rotation and multi-client access.

Example:

```
API_TOKENS=ABC123,XYZ789
```

## Example API Request

```
curl -X POST \
  -H "Authorization: Bearer ABC123" \
  -F "file=@image.jpg" \
  http://localhost:8000/remove-background
```

Adjust the endpoint path according to your API implementation.

## License

Licensed under the Apache License 2.0.
See the LICENSE file for details.

## Support

Official withoutBG documentation:

[https://withoutbg.com/documentation](https://withoutbg.com/documentation)

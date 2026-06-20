# Scalable API with Advanced Rate Limiting and Observability

A robust backend API service demonstrating advanced rate limiting (Token Bucket), structured logging, and comprehensive observability (Prometheus & Grafana) orchestrated with Docker Compose.

## Architecture
- **Framework**: Python 3.9 + FastAPI
- **Rate Limiting**: Token Bucket algorithm backed by Redis
- **Metrics**: Prometheus client exposed via `/metrics`
- **Logging**: Structured JSON logging (`python-json-logger`)
- **Containerization**: Multi-stage Docker builds & `docker-compose`

## Setup & Installation

1. Ensure Docker and Docker Compose are installed.
2. Clone this repository.
3. Start the services:
   ```bash
   docker-compose up --build -d
   ```

## Services Overview

- **API**: http://localhost:8081
- **Redis**: localhost:6379
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (User: `admin`, Password: `admin`)

## API Endpoints

### 1. Health Status
- **GET** `/api/status`
- **Returns**: `200 OK`, `{"status": "healthy"}`

### 2. Products (CRUD)
- **POST** `/api/products`
  - **Body**: `{"name": "string", "description": "string", "price": 10.5}`
  - **Returns**: `201 Created`
- **GET** `/api/products`
  - **Returns**: `200 OK`, list of products.

### 3. Protected Action (Rate Limited)
- **POST** `/api/protected-action`
  - **Returns**: `200 OK` on success. `429 Too Many Requests` when limits are exceeded.
  - **Headers**:
    - `X-RateLimit-Limit`: The configured capacity (default 10)
    - `X-RateLimit-Remaining`: Remaining tokens
    - `X-RateLimit-Reset`: Unix timestamp when the bucket fully refills

## Rate Limiting
The API uses the **Token Bucket** algorithm implemented as a FastAPI dependency. It connects to Redis using pipelined transactions to atomically read and update the bucket's tokens and timestamp based on the client's IP address. Configuration is handled via environment variables (`RATE_LIMIT_CAPACITY`, `RATE_LIMIT_REFILL_RATE`).

## Testing
Tests are written with `pytest` and `httpx`.
To run tests, make sure the services are running and execute:
```bash
docker-compose exec api pytest api/src/tests -v
```

## Observability Dashboards
Grafana is pre-configured with a Prometheus data source and an **API Observability Dashboard** visualizing:
- API Request Rates
- Rate Limit Hits (429 status codes)

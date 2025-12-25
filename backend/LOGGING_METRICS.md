# Logging and Metrics Guide

This document describes the structured logging and metrics infrastructure implemented in the Navio Academic Advisor API.

## Overview

The application now includes:
- **Structured logging** with JSON format support for production
- **Request ID tracking** for distributed tracing
- **Request logging middleware** with timing and status codes
- **Enhanced health checks** with database connectivity
- **Metrics endpoint** with system and application statistics

## Features Implemented

### 1. Structured Logging

**Location**: `app/core/logging_config.py`

The application uses a custom JSON formatter that outputs structured logs for easier parsing in production environments.

**Configuration**:
```python
from app.core.logging_config import setup_logging

# Development (human-readable)
logger = setup_logging(use_json=False)

# Production (JSON structured logs)
logger = setup_logging(use_json=True)
```

**Log Fields**:
- `timestamp`: ISO 8601 UTC timestamp
- `level`: Log level (INFO, WARNING, ERROR, etc.)
- `logger`: Logger name
- `message`: Log message
- `module`: Python module name
- `function`: Function name
- `line`: Line number
- `request_id`: Unique request identifier (if available)
- `method`: HTTP method (if request context)
- `path`: Request path (if request context)
- `status_code`: HTTP status code (if request context)
- `duration_ms`: Request duration in milliseconds (if request context)
- `client_ip`: Client IP address (if request context)
- `exception`: Exception details (if error)

**Example JSON Log**:
```json
{
  "timestamp": "2025-12-25T10:30:45.123Z",
  "level": "INFO",
  "logger": "navio",
  "message": "GET /api/recommend - 200 - 125.45ms",
  "module": "middleware",
  "function": "dispatch",
  "line": 95,
  "request_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
  "method": "GET",
  "path": "/api/recommend",
  "status_code": 200,
  "duration_ms": 125.45,
  "client_ip": "127.0.0.1"
}
```

### 2. Request ID Middleware

**Location**: `app/core/middleware.py`

Every request is assigned a unique ID for tracing across logs and services.

**Features**:
- Auto-generates UUID for each request
- Preserves `X-Request-ID` header if provided by client
- Adds request ID to response headers
- Stores request ID in context for access throughout request lifecycle

**Usage**:
```python
from app.core.middleware import get_request_id

# In any route or service
request_id = get_request_id()
logger.info("Processing request", extra={"request_id": request_id})
```

### 3. Request Logging Middleware

**Location**: `app/core/middleware.py`

Automatically logs all HTTP requests with timing information.

**Logged Information**:
- HTTP method and path
- Status code
- Response time in milliseconds
- Client IP address
- Request ID

**Example Log Output**:
```
2025-12-25 10:30:45 - navio - INFO - POST /api/recommend - 200 - 125.45ms
```

### 4. Health Check Endpoints

**Location**: `app/api/routes/health.py`

#### GET `/health`
Comprehensive health check with database connectivity test.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-25T10:30:45.123Z",
  "checks": {
    "database": {
      "status": "healthy",
      "message": "Database connection successful"
    }
  }
}
```

**Status Codes**:
- `200 OK`: All checks passed
- `503 Service Unavailable`: One or more checks failed

#### GET `/health/live`
Kubernetes liveness probe - simple check that app is running.

**Response**:
```json
{
  "status": "alive",
  "timestamp": "2025-12-25T10:30:45.123Z"
}
```

#### GET `/health/ready`
Kubernetes readiness probe - checks if app is ready to serve traffic.

**Response**:
```json
{
  "status": "ready",
  "timestamp": "2025-12-25T10:30:45.123Z",
  "checks": {
    "database": "ready"
  }
}
```

### 5. Metrics Endpoint

**Location**: `app/api/routes/health.py`

#### GET `/metrics`
Returns application and system metrics.

**Response**:
```json
{
  "timestamp": "2025-12-25T10:30:45.123Z",
  "uptime_seconds": 3600.5,
  "system": {
    "cpu_percent": 25.5,
    "memory": {
      "total_gb": 16.0,
      "available_gb": 8.5,
      "used_percent": 46.9
    },
    "disk": {
      "total_gb": 500.0,
      "free_gb": 250.0,
      "used_percent": 50.0
    }
  },
  "database": {
    "programs": 6,
    "courses": 150,
    "requirements": 45,
    "embeddings": 195
  }
}
```

## Configuration

### Enable JSON Logging in Production

Update `app/main.py`:
```python
# Production configuration
logger = setup_logging(use_json=True)
```

### Environment Variables

No additional environment variables required. The system uses existing database configuration from settings.

## Testing

New test suite added in `tests/test_health_metrics.py`:

**Run health and metrics tests**:
```bash
pytest tests/test_health_metrics.py -v
```

**Test coverage**:
- Health check endpoint
- Liveness probe
- Readiness probe
- Metrics endpoint
- Request ID middleware
- Root endpoint

## Monitoring Integration

### Prometheus

The metrics endpoint can be scraped by Prometheus. Example configuration:

```yaml
scrape_configs:
  - job_name: 'navio-api'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['api.example.com:8000']
```

### Log Aggregation

With JSON logging enabled, logs can be easily ingested by:
- **Elasticsearch/ELK Stack**: Parse JSON logs directly
- **CloudWatch**: AWS log parsing and filtering
- **Datadog**: Structured log analysis
- **Splunk**: JSON sourcetype configuration

### Example Log Query (Elasticsearch)

```json
{
  "query": {
    "bool": {
      "must": [
        {"match": {"level": "ERROR"}},
        {"range": {"duration_ms": {"gte": 1000}}}
      ]
    }
  }
}
```

## Middleware Order

Middleware is added in reverse execution order. Current stack:

1. **RequestIDMiddleware**: Adds unique ID to each request
2. **RequestLoggingMiddleware**: Logs request timing and status
3. **RateLimitMiddleware**: Enforces rate limits
4. **CORSMiddleware**: Handles cross-origin requests

## Best Practices

### Logging in Application Code

Always include structured data with log messages:

```python
import logging

logger = logging.getLogger("navio")

# Good: Structured logging
logger.info(
    "User authenticated successfully",
    extra={
        "user_id": user.id,
        "request_id": get_request_id(),
    }
)

# Avoid: String formatting in message
logger.info(f"User {user.id} authenticated")  # Harder to parse
```

### Error Logging

Include exception information for better debugging:

```python
try:
    result = process_data()
except Exception as e:
    logger.exception(
        "Failed to process data",
        extra={
            "request_id": get_request_id(),
            "data_id": data.id,
        }
    )
    raise
```

### Performance Monitoring

Track operation timing:

```python
import time

start_time = time.time()
result = expensive_operation()
duration_ms = (time.time() - start_time) * 1000

logger.info(
    "Operation completed",
    extra={
        "operation": "expensive_operation",
        "duration_ms": duration_ms,
    }
)
```

## Troubleshooting

### No Request ID in Logs

Ensure `RequestIDMiddleware` is added to the app:
```python
app.add_middleware(RequestIDMiddleware)
```

### Health Check Fails

Check database connectivity:
```bash
# Test database connection
psql $DATABASE_URL -c "SELECT 1"
```

### JSON Logs Not Appearing

Verify JSON logging is enabled:
```python
logger = setup_logging(use_json=True)
```

## Future Enhancements

Potential improvements for production:

1. **Custom Metrics**: Add Prometheus-compatible metrics endpoint
2. **Distributed Tracing**: Integrate OpenTelemetry for cross-service tracing
3. **Log Sampling**: Implement sampling for high-traffic endpoints
4. **Performance Metrics**: Track individual endpoint latencies
5. **Error Rate Alerts**: Configure alerting based on error count thresholds
6. **Redis Metrics**: Add Redis health check if caching is implemented

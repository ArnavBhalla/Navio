"""
Middleware for request tracking, logging, and metrics
"""
import time
import uuid
import logging
from typing import Callable
from contextvars import ContextVar

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# Context variable to store request ID across async contexts
request_id_context: ContextVar[str] = ContextVar("request_id", default=None)

logger = logging.getLogger("navio")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add unique request ID to each request"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Store in context var for access in other parts of the app
        request_id_context.set(request_id)

        # Add to request state for easy access
        request.state.request_id = request_id

        # Process request
        response = await call_next(request)

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests with timing information"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.request_count = 0
        self.error_count = 0

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Start timer
        start_time = time.time()

        # Get request metadata
        request_id = getattr(request.state, "request_id", None)
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path

        # Increment request counter
        self.request_count += 1

        # Process request
        try:
            response = await call_next(request)
            status_code = response.status_code

            # Increment error counter for 4xx and 5xx
            if status_code >= 400:
                self.error_count += 1

        except Exception as exc:
            # Log exception and re-raise
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                f"Request failed: {method} {path}",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "client_ip": client_ip,
                    "duration_ms": duration_ms,
                },
                exc_info=True,
            )
            self.error_count += 1
            raise

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Log request with structured data
        log_level = logging.WARNING if status_code >= 400 else logging.INFO
        logger.log(
            log_level,
            f"{method} {path} - {status_code} - {duration_ms:.2f}ms",
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration_ms": round(duration_ms, 2),
                "client_ip": client_ip,
            },
        )

        return response

    def get_metrics(self) -> dict:
        """Get current metrics"""
        return {
            "total_requests": self.request_count,
            "total_errors": self.error_count,
        }


def get_request_id() -> str:
    """Get the current request ID from context"""
    return request_id_context.get()

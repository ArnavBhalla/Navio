from datetime import timedelta
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.core.rate_limit import InMemoryRateLimiter, RateLimitRule, rate_limit_key_from_request
from app.api.routes import recommend, search, seed, auth

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("navio")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple per-process rate limiting middleware."""

    def __init__(self, app, limiter: InMemoryRateLimiter):
        super().__init__(app)
        self.limiter = limiter

    async def dispatch(self, request: Request, call_next):
        # Skip health and docs to keep them always available
        path = request.url.path
        if path.startswith("/health") or path.startswith("/docs") or path.startswith("/openapi"):
            return await call_next(request)

        key = rate_limit_key_from_request(request)
        try:
            self.limiter.check(key)
        except Exception as exc:
            from fastapi import HTTPException, status

            if isinstance(exc, HTTPException):
                # Let FastAPI handle HTTPException (e.g. 429)
                raise exc
            # Fallback: treat as generic 429
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
            )

        return await call_next(request)


app = FastAPI(
    title="Navio Academic Advisor API",
    description="AI-powered course recommendation system",
    version="1.0.0",
)

# CORS middleware
app.addMiddleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiter: 60 requests per minute per IP+path
rate_limiter = InMemoryRateLimiter(
    rule=RateLimitRule(requests=60, window=timedelta(minutes=1))
)
app.add_middleware(RateLimitMiddleware, limiter=rate_limiter)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return a consistent structure for validation errors."""
    logger.warning(f"Validation error on {request.url}: {exc}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Request validation failed",
            "errors": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Catch-all handler to avoid leaking internals in responses."""
    logger.exception(f"Unhandled error on {request.method} {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Include routers
app.include_router(auth.router, tags=["auth"])
app.include_router(recommend.router, prefix="/api", tags=["recommend"])
app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(seed.router, prefix="/api", tags=["seed"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info("Starting up application, initializing database...")
    init_db()
    logger.info("Database initialization complete.")


@app.get("/")
async def root():
    return {
        "message": "Navio Academic Advisor API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

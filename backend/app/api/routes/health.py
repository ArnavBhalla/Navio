"""
Health check and metrics endpoints
"""
import time
import psutil
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db

router = APIRouter()

# Track application start time
START_TIME = time.time()


@router.get("/health", tags=["health"])
async def health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Comprehensive health check endpoint

    Checks:
    - API is responding
    - Database connectivity
    - Database can execute queries

    Returns:
        Health status with component checks
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "checks": {},
    }

    # Check database connectivity
    db_healthy = True
    db_details = {}

    try:
        # Try to execute a simple query
        result = db.execute(text("SELECT 1"))
        result.fetchone()
        db_details["status"] = "healthy"
        db_details["message"] = "Database connection successful"
    except Exception as e:
        db_healthy = False
        db_details["status"] = "unhealthy"
        db_details["message"] = f"Database error: {str(e)}"
        health_status["status"] = "unhealthy"

    health_status["checks"]["database"] = db_details

    # Set appropriate HTTP status code
    status_code = status.HTTP_200_OK if db_healthy else status.HTTP_503_SERVICE_UNAVAILABLE

    return health_status


@router.get("/health/live", tags=["health"])
async def liveness_check() -> Dict[str, str]:
    """
    Kubernetes liveness probe endpoint
    Simple check that the application is running
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/health/ready", tags=["health"])
async def readiness_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Kubernetes readiness probe endpoint
    Checks if the application is ready to serve traffic
    """
    ready = True
    checks = {}

    # Check database
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = "ready"
    except Exception as e:
        ready = False
        checks["database"] = f"not ready: {str(e)}"

    return {
        "status": "ready" if ready else "not ready",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "checks": checks,
    }


@router.get("/metrics", tags=["metrics"])
async def metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Application metrics endpoint

    Returns:
        Application statistics and system metrics
    """
    uptime_seconds = time.time() - START_TIME

    # Get system metrics
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    # Get database stats
    db_stats = {}
    try:
        # Count total programs
        programs_count = db.execute(text("SELECT COUNT(*) FROM programs")).scalar()
        courses_count = db.execute(text("SELECT COUNT(*) FROM courses")).scalar()
        requirements_count = db.execute(text("SELECT COUNT(*) FROM requirements")).scalar()
        embeddings_count = db.execute(text("SELECT COUNT(*) FROM embeddings")).scalar()

        db_stats = {
            "programs": programs_count,
            "courses": courses_count,
            "requirements": requirements_count,
            "embeddings": embeddings_count,
        }
    except Exception as e:
        db_stats = {"error": str(e)}

    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "uptime_seconds": round(uptime_seconds, 2),
        "system": {
            "cpu_percent": cpu_percent,
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_percent": memory.percent,
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "used_percent": disk.percent,
            },
        },
        "database": db_stats,
    }

"""
Database seeding API endpoint (development only)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
import subprocess
from pathlib import Path
from app.core.security import require_roles, User

router = APIRouter()


@router.post("/seed")
async def seed_database(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"])),
):
    """
    Trigger database seeding (development only)

    WARNING: This will delete all existing data and reload from seed files
    """

    # Only allow in development
    if settings.ENVIRONMENT != "development":
        raise HTTPException(
            status_code=403,
            detail="Seeding is only available in development environment"
        )

    try:
        # Run the seed script
        script_path = Path(__file__).parent.parent.parent.parent / "scripts" / "seed_database.py"

        result = subprocess.run(
            ["python", str(script_path)],
            capture_output=True,
            text=True,
            check=True
        )

        return {
            "status": "success",
            "message": "Database seeded successfully",
            "output": result.stdout
        }

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Seeding failed: {e.stderr}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )

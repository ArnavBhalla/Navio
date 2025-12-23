"""
Authentication endpoints (JWT with roles).
"""
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.core.config import settings
from app.core.security import create_access_token


router = APIRouter()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def authenticate_demo_user(username: str, password: str):
    """
    Simple demo authentication against credentials defined in settings.

    In a production system this would query a user database and verify
    hashed passwords.
    """
    # Admin user
    if (
        username == settings.DEMO_ADMIN_USERNAME
        and password == settings.DEMO_ADMIN_PASSWORD
    ):
        return {"username": username, "roles": ["admin", "user"]}

    # Regular demo user
    if (
        username == settings.DEMO_USER_USERNAME
        and password == settings.DEMO_USER_PASSWORD
    ):
        return {"username": username, "roles": ["user"]}

    return None


@router.post("/auth/token", response_model=TokenResponse)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> TokenResponse:
    """
    Obtain a JWT access token using username/password.

    - Uses demo credentials from settings:
      - DEMO_ADMIN_USERNAME / DEMO_ADMIN_PASSWORD (role: admin,user)
      - DEMO_USER_USERNAME / DEMO_USER_PASSWORD (role: user)
    """
    user = authenticate_demo_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = create_access_token(
        subject=user["username"],
        roles=user["roles"],
        expires_minutes=access_token_expires.seconds // 60
        if access_token_expires
        else None,
    )

    return TokenResponse(access_token=access_token)



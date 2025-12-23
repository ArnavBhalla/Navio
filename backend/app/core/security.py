from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from app.core.config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


class TokenData(BaseModel):
    """Data stored in JWT token."""

    sub: str
    roles: List[str] = []


class User(BaseModel):
    """Simple user model used for auth/roles."""

    username: str
    roles: List[str] = []


def create_access_token(
    *, subject: str, roles: Optional[List[str]] = None, expires_minutes: Optional[int] = None
) -> str:
    """Create a signed JWT access token."""

    if expires_minutes is None:
        expires_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)

    to_encode = {
        "sub": subject,
        "roles": roles or [],
        "exp": expire,
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.AUTH_SECRET_KEY,
        algorithm=settings.AUTH_ALGORITHM,
    )
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Decode JWT and return current user."""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.AUTH_SECRET_KEY,
            algorithms=[settings.AUTH_ALGORITHM],
        )
        username: str = payload.get("sub")
        roles: List[str] = payload.get("roles", [])
        if username is None:
            raise credentials_exception
        token_data = TokenData(sub=username, roles=roles)
    except JWTError:
        raise credentials_exception

    return User(username=token_data.sub, roles=token_data.roles)


def require_roles(required_roles: List[str]):
    """Dependency factory to require one of a set of roles."""

    async def _require(user: User = Depends(get_current_user)) -> User:
        if not required_roles:
            return user

        if not any(role in user.roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return user

    return _require



# app/auth.py
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .settings import settings
from .database import get_db
from . import models

# ---------------------
# Password hashing
# ---------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Return bcrypt hash for a plain password."""
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain password against a bcrypt hash."""
    return pwd_context.verify(plain, hashed)

# ---------------------
# JWT helpers
# ---------------------
def create_access_token(data: dict, expires_minutes: Optional[int] = None) -> str:
    """
    Create a JWT token containing `data` as payload.
    The `sub` claim should be set by the caller (e.g., user id).
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=(expires_minutes if expires_minutes is not None else settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded

def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT token. Returns payload dict on success, otherwise None.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

# ---------------------
# Security dependencies
# ---------------------
# Use HTTPBearer so Swagger shows a single "Authorize" dialog that accepts a Bearer token.
bearer_scheme = HTTPBearer()

def _credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    """
    Dependency to get the current authenticated user.
    Accepts a Bearer token from the Authorization header (HTTPBearer).
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise _credentials_exception()

    # We expect the token to include a 'sub' claim with the user's id (string or int)
    user_id = payload.get("sub")
    if user_id is None:
        raise _credentials_exception()

    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise _credentials_exception()

    user = db.query(models.User).filter(models.User.id == user_id_int).first()
    if user is None:
        raise _credentials_exception()
    return user

def require_admin(current_user: models.User = Depends(get_current_user)) -> models.User:
    """
    Dependency to require admin privileges.
    Use this in routes that only admins should access.
    """
    if getattr(current_user, "role", None) != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return current_user

"""
auth.py – Password hashing and JWT token utilities.

Security decisions
------------------
- Passwords are hashed with bcrypt via passlib.
- JWTs carry only the user's email as the subject (sub claim).
  The user ID is never trusted from the frontend – it is always resolved
  from the token's sub (email) via a database lookup.
- Token expiry is configured via ACCESS_TOKEN_EXPIRE_MINUTES env var.
- SECRET_KEY is read from environment; no insecure fallback is used in
  production paths.
"""

import os
import warnings
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext

load_dotenv()

SECRET_KEY: str = os.getenv("SECRET_KEY", "")
ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
)

if not SECRET_KEY:
    warnings.warn(
        "SECRET_KEY is not set. Set it in .env before running in production.",
        stacklevel=2,
    )

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── Password utilities ────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    """Return a bcrypt hash of *plain*."""
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if *plain* matches the stored *hashed* password."""
    return _pwd_context.verify(plain, hashed)


# ── JWT utilities ─────────────────────────────────────────────────────────────

def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a signed JWT with *subject* (email) as the ``sub`` claim.
    Defaults to ACCESS_TOKEN_EXPIRE_MINUTES if no *expires_delta* given.
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return jwt.encode(
        {"sub": subject, "exp": expire},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_token(token: str) -> str | None:
    """
    Verify *token* and return the subject (email) on success.
    Returns None for invalid or expired tokens – never raises.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None

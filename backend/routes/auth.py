"""
routes/auth.py – Registration and login endpoints.

POST /auth/register   – create a new user account
POST /auth/login      – verify credentials, return JWT
GET  /auth/me         – return the authenticated user's identity
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.database import get_db
from backend.models.db_models import User
from backend.models.schemas import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserOut,
)
from backend.services.auth import hash_password, verify_password, create_access_token, decode_token

router = APIRouter(prefix="/auth", tags=["auth"])
_bearer = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency that resolves the JWT bearer token to a User ORM object.
    Raises 401 for missing, invalid, expired, or unrecognised tokens.
    The user ID is never trusted from the client – identity is always
    verified against the database using the token's sub (email).
    """
    token = credentials.credentials
    email = decode_token(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
        )
    return user


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register(body: RegisterRequest, db: Session = Depends(get_db)) -> UserOut:
    """
    Create a new user account.
    Returns 409 if the email is already registered.
    Passwords are stored as bcrypt hashes – never as plain text.
    """
    user = User(
        name=body.name,
        email=body.email.lower(),
        password_hash=hash_password(body.password),
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email address already exists.",
        )
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and obtain a JWT",
)
def login(body: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """
    Verify credentials and return a bearer token.
    Returns a generic 401 for both bad email and bad password to avoid
    leaking which part of the credential is wrong.
    """
    user = db.query(User).filter(User.email == body.email.lower()).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )
    token = create_access_token(subject=user.email)
    return TokenResponse(access_token=token)


@router.get(
    "/me",
    response_model=UserOut,
    summary="Return the authenticated user's profile",
)
def me(current_user: User = Depends(get_current_user)) -> UserOut:
    """Return basic identity info for the bearer-token holder."""
    return current_user

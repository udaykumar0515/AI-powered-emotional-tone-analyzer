"""
routes/profile.py – Authenticated profile endpoints.

GET  /profile/        – retrieve the current user's profile
PUT  /profile/        – update the current user's name

Access control: each route resolves the caller's identity from the JWT.
A user can only read and update their own profile – no user ID is accepted
from the request body or URL.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.db_models import User
from backend.models.schemas import UserOut, ProfileUpdateRequest
from backend.routes.auth import get_current_user

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get(
    "/",
    response_model=UserOut,
    summary="Retrieve the authenticated user's profile",
)
def get_profile(current_user: User = Depends(get_current_user)) -> UserOut:
    """Return name, email, and registration date for the bearer-token holder."""
    return current_user


@router.put(
    "/",
    response_model=UserOut,
    summary="Update the authenticated user's name",
)
def update_profile(
    body: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserOut:
    """
    Update the display name of the bearer-token holder.
    Only the name field is editable at this milestone.
    Email changes are not supported.
    """
    current_user.name = body.name
    try:
        db.commit()
        db.refresh(current_user)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save profile changes.",
        )
    return current_user

"""
db_models.py – SQLAlchemy ORM model definitions (Milestone 1: users only).
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from backend.database import Base


class User(Base):
    """
    Represents a registered user.

    Columns
    -------
    id            : auto-increment primary key
    name          : display name (required)
    email         : unique login identifier
    password_hash : bcrypt hash – plain-text passwords are never stored
    created_at    : UTC timestamp set on INSERT
    """

    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name: str = Column(String(120), nullable=False)
    email: str = Column(String(255), unique=True, nullable=False, index=True)
    password_hash: str = Column(String(255), nullable=False)
    created_at: datetime = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User id={self.id} email={self.email!r}>"

"""
schemas.py – Pydantic request/response schemas.

Passwords and hashes are never included in response models.
"""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator


# ── Auth ─────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120, examples=["Alice"])
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name must not be blank.")
        return v.strip()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── User / Profile ────────────────────────────────────────────────────────────

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ProfileUpdateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name must not be blank.")
        return v.strip()


# ── Sentiment ─────────────────────────────────────────────────────────────────

class SentimentRequest(BaseModel):
    text: str = Field(..., min_length=1)


class SingleSentimentResult(BaseModel):
    original_text: str
    processed_text: str
    sentiment_label: str        # Positive | Negative | Neutral
    compound_score: float
    positive_score: float
    negative_score: float
    neutral_score: float


class SentimentResponse(BaseModel):
    results: list[SingleSentimentResult]
    summary: dict[str, int]     # {"Positive": n, "Negative": n, "Neutral": n}

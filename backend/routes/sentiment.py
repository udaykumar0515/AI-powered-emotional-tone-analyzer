"""
routes/sentiment.py – Sentiment analysis endpoint.

POST /sentiment/analyze        – analyse one text string
POST /sentiment/analyze-file   – analyse text uploaded as .txt or .csv
"""

import io
import csv
import chardet

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.models.db_models import User
from backend.models.schemas import (
    SentimentRequest,
    SentimentResponse,
    SingleSentimentResult,
)
from backend.routes.auth import get_current_user
from backend.services import nlp

router = APIRouter(prefix="/sentiment", tags=["sentiment"])

_MAX_FILE_BYTES = 2 * 1024 * 1024   # 2 MB
_MAX_CSV_ROWS   = 500


def _build_response(results: list[dict]) -> SentimentResponse:
    """Convert raw nlp.analyse() dicts to SentimentResponse."""
    items = [SingleSentimentResult(**r) for r in results]
    summary: dict[str, int] = {"Positive": 0, "Negative": 0, "Neutral": 0}
    for item in items:
        summary[item.sentiment_label] += 1
    return SentimentResponse(results=items, summary=summary)


# ── Text string analysis ──────────────────────────────────────────────────────

@router.post(
    "/analyze",
    response_model=SentimentResponse,
    summary="Analyse a single text string",
)
def analyze_text(
    body: SentimentRequest,
    _current_user: User = Depends(get_current_user),
) -> SentimentResponse:
    """
    Validate and analyse one piece of text.
    Returns 422 if the text is empty or whitespace-only.
    """
    if not body.text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Text must not be empty or whitespace only.",
        )
    result = nlp.analyse(body.text)
    return _build_response([result])


# ── File upload analysis ──────────────────────────────────────────────────────

@router.post(
    "/analyze-file",
    response_model=SentimentResponse,
    summary="Analyse text from an uploaded .txt or .csv file",
)
async def analyze_file(
    file: UploadFile = File(...),
    csv_column: str = Form(default=""),
    _current_user: User = Depends(get_current_user),
) -> SentimentResponse:
    """
    Accept a .txt or .csv file and return sentiment for each valid text row.

    For .txt  – the entire file content is treated as one text block.
    For .csv  – each non-empty row in the selected column is analysed.
                The caller may pass ``csv_column`` to specify which column
                to use; if omitted, the first column is used.
    """
    filename = (file.filename or "").lower()
    if not filename.endswith((".txt", ".csv")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .txt and .csv files are supported.",
        )

    raw = await file.read()
    if not raw:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty.",
        )
    if len(raw) > _MAX_FILE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds the 2 MB limit.",
        )

    # Detect encoding
    detected = chardet.detect(raw)
    encoding = detected.get("encoding") or "utf-8"

    try:
        text_content = raw.decode(encoding, errors="replace")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not decode the file. Ensure it is a valid text file.",
        )

    # ── .txt ──────────────────────────────────────────────────────────────────
    if filename.endswith(".txt"):
        stripped = text_content.strip()
        if not stripped:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="The uploaded .txt file contains no readable text.",
            )
        return _build_response([nlp.analyse(stripped)])

    # ── .csv ──────────────────────────────────────────────────────────────────
    reader = csv.DictReader(io.StringIO(text_content))
    headers = reader.fieldnames

    if not headers:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The CSV file has no headers or is empty.",
        )

    # Resolve the target column
    target_col: str
    if csv_column and csv_column in headers:
        target_col = csv_column
    elif csv_column and csv_column not in headers:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Column '{csv_column}' not found. Available columns: {list(headers)}",
        )
    else:
        target_col = headers[0]

    texts: list[str] = []
    for i, row in enumerate(reader):
        if i >= _MAX_CSV_ROWS:
            break
        cell = row.get(target_col, "")
        if cell and cell.strip():
            texts.append(cell.strip())

    if not texts:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"No valid text found in column '{target_col}'.",
        )

    results = nlp.analyse_many(texts)
    return _build_response(results)

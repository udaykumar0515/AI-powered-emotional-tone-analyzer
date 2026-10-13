"""
api_client.py – Thin HTTP wrapper around the FastAPI backend.

All Streamlit pages call this module instead of making raw requests.
It reads BACKEND_URL from environment (defaults to localhost:8000).
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL: str = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
_TIMEOUT = 10  # seconds


def _headers(token: str | None = None) -> dict:
    h = {"Content-Type": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


# ── Auth ──────────────────────────────────────────────────────────────────────

def register(name: str, email: str, password: str) -> dict:
    r = requests.post(
        f"{BASE_URL}/auth/register",
        json={"name": name, "email": email, "password": password},
        timeout=_TIMEOUT,
    )
    return {"status_code": r.status_code, "data": r.json()}


def login(email: str, password: str) -> dict:
    r = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": email, "password": password},
        timeout=_TIMEOUT,
    )
    return {"status_code": r.status_code, "data": r.json()}


def get_me(token: str) -> dict:
    r = requests.get(
        f"{BASE_URL}/auth/me",
        headers=_headers(token),
        timeout=_TIMEOUT,
    )
    return {"status_code": r.status_code, "data": r.json()}


# ── Profile ───────────────────────────────────────────────────────────────────

def get_profile(token: str) -> dict:
    r = requests.get(
        f"{BASE_URL}/profile/",
        headers=_headers(token),
        timeout=_TIMEOUT,
    )
    return {"status_code": r.status_code, "data": r.json()}


def update_profile(token: str, name: str) -> dict:
    r = requests.put(
        f"{BASE_URL}/profile/",
        json={"name": name},
        headers=_headers(token),
        timeout=_TIMEOUT,
    )
    return {"status_code": r.status_code, "data": r.json()}


# ── Sentiment ─────────────────────────────────────────────────────────────────

def analyze_text(token: str, text: str) -> dict:
    r = requests.post(
        f"{BASE_URL}/sentiment/analyze",
        json={"text": text},
        headers=_headers(token),
        timeout=_TIMEOUT,
    )
    return {"status_code": r.status_code, "data": r.json()}


def analyze_file(token: str, file_bytes: bytes, filename: str, csv_column: str = "") -> dict:
    # multipart/form-data – do not pass Content-Type header (requests sets boundary)
    auth_header = {"Authorization": f"Bearer {token}"}
    r = requests.post(
        f"{BASE_URL}/sentiment/analyze-file",
        files={"file": (filename, file_bytes, "application/octet-stream")},
        data={"csv_column": csv_column},
        headers=auth_header,
        timeout=_TIMEOUT,
    )
    return {"status_code": r.status_code, "data": r.json()}


# ── Health ────────────────────────────────────────────────────────────────────

def health() -> bool:
    """Return True if the backend is reachable."""
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=4)
        return r.status_code == 200
    except requests.exceptions.RequestException:
        return False

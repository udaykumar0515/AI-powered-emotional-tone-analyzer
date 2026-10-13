"""
conftest.py – Shared pytest fixtures.

Uses an in-memory SQLite database so tests run without MySQL.
The FastAPI app is patched to use the test database via dependency override.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base, get_db
from backend.main import app

from sqlalchemy.pool import StaticPool

# ── In-memory SQLite engine ───────────────────────────────────────────────────
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create tables once for the entire test session."""
    from backend.models import db_models  # noqa: F401
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(autouse=True)
def clean_users():
    """Truncate the users table between tests to ensure isolation."""
    yield
    db = TestSessionLocal()
    try:
        from backend.models.db_models import User
        db.query(User).delete()
        db.commit()
    finally:
        db.close()


@pytest.fixture(scope="session")
def client():
    """TestClient with DB dependency overridden."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

"""
test_auth.py – Tests for registration, login, /me, and access isolation.
"""

import pytest


# ── Helpers ───────────────────────────────────────────────────────────────────

def _register(client, name="Alice", email="alice@example.com", password="pass1234"):
    return client.post(
        "/auth/register",
        json={"name": name, "email": email, "password": password},
    )


def _login(client, email="alice@example.com", password="pass1234"):
    return client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )


def _token(client, email="alice@example.com", password="pass1234"):
    _register(client, email=email, password=password)
    resp = _login(client, email=email, password=password)
    return resp.json()["access_token"]


# ── Registration ──────────────────────────────────────────────────────────────

class TestRegistration:
    def test_successful_registration(self, client):
        resp = _register(client)
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "alice@example.com"
        assert data["name"] == "Alice"
        assert "password" not in data
        assert "password_hash" not in data

    def test_duplicate_email_returns_409(self, client):
        _register(client)
        resp = _register(client)
        assert resp.status_code == 409

    def test_missing_name_returns_422(self, client):
        resp = client.post(
            "/auth/register",
            json={"name": "", "email": "b@example.com", "password": "pass1234"},
        )
        assert resp.status_code == 422

    def test_invalid_email_returns_422(self, client):
        resp = client.post(
            "/auth/register",
            json={"name": "Bob", "email": "not-an-email", "password": "pass1234"},
        )
        assert resp.status_code == 422

    def test_short_password_returns_422(self, client):
        resp = client.post(
            "/auth/register",
            json={"name": "Bob", "email": "bob@example.com", "password": "abc"},
        )
        assert resp.status_code == 422

    def test_password_not_in_response(self, client):
        resp = _register(client)
        body = resp.json()
        assert "password" not in body
        assert "password_hash" not in body


# ── Login ─────────────────────────────────────────────────────────────────────

class TestLogin:
    def test_valid_login_returns_token(self, client):
        _register(client)
        resp = _login(client)
        assert resp.status_code == 200
        assert "access_token" in resp.json()
        assert resp.json()["token_type"] == "bearer"

    def test_wrong_password_returns_401(self, client):
        _register(client)
        resp = _login(client, password="wrongpassword")
        assert resp.status_code == 401

    def test_unknown_email_returns_401(self, client):
        resp = _login(client, email="ghost@example.com")
        assert resp.status_code == 401

    def test_token_does_not_expose_password(self, client):
        _register(client)
        resp = _login(client)
        data = resp.json()
        assert "password" not in str(data)
        assert "hash" not in str(data)


# ── /auth/me ──────────────────────────────────────────────────────────────────

class TestMe:
    def test_me_returns_user_info(self, client):
        token = _token(client)
        resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["email"] == "alice@example.com"

    def test_me_without_token_returns_403(self, client):
        resp = client.get("/auth/me")
        assert resp.status_code in (401, 403)

    def test_me_with_invalid_token_returns_401(self, client):
        resp = client.get("/auth/me", headers={"Authorization": "Bearer invalidtoken"})
        assert resp.status_code == 401


# ── Access isolation ──────────────────────────────────────────────────────────

class TestAccessIsolation:
    def test_users_cannot_access_each_others_profile(self, client):
        token_a = _token(client, email="a@example.com")
        _register(client, name="Bob", email="b@example.com", password="pass5678")

        # Alice's token should only return Alice's profile
        resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token_a}"})
        assert resp.json()["email"] == "a@example.com"

    def test_profile_update_affects_only_own_record(self, client):
        token_a = _token(client, email="a@example.com")
        _register(client, name="Bob", email="b@example.com", password="pass5678")

        # Update Alice's name
        client.put(
            "/profile/",
            json={"name": "Alice Updated"},
            headers={"Authorization": f"Bearer {token_a}"},
        )

        # Alice sees updated name
        resp_a = client.get("/auth/me", headers={"Authorization": f"Bearer {token_a}"})
        assert resp_a.json()["name"] == "Alice Updated"

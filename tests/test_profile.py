"""
test_profile.py – Tests for profile retrieval and update endpoints.
"""


def _register_and_login(client, email="user@example.com", password="pass1234"):
    client.post(
        "/auth/register",
        json={"name": "User", "email": email, "password": password},
    )
    resp = client.post("/auth/login", json={"email": email, "password": password})
    return resp.json()["access_token"]


class TestProfile:
    def test_get_profile_returns_correct_fields(self, client):
        token = _register_and_login(client)
        resp = client.get("/profile/", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        assert "name" in data
        assert "email" in data
        assert "created_at" in data
        assert "password" not in data
        assert "password_hash" not in data

    def test_update_name_succeeds(self, client):
        token = _register_and_login(client)
        resp = client.put(
            "/profile/",
            json={"name": "New Name"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "New Name"

    def test_update_blank_name_returns_422(self, client):
        token = _register_and_login(client)
        resp = client.put(
            "/profile/",
            json={"name": "   "},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 422

    def test_profile_without_token_is_rejected(self, client):
        resp = client.get("/profile/")
        assert resp.status_code in (401, 403)

    def test_update_without_token_is_rejected(self, client):
        resp = client.put("/profile/", json={"name": "Hacker"})
        assert resp.status_code in (401, 403)

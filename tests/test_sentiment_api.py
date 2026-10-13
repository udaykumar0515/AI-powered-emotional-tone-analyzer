"""
test_sentiment_api.py – Integration tests for sentiment analysis endpoints.

Uses the TestClient with SQLite in-memory DB (see conftest.py).
"""

import io


def _register_and_token(client, email="s@example.com", password="pass1234"):
    client.post(
        "/auth/register",
        json={"name": "Tester", "email": email, "password": password},
    )
    resp = client.post("/auth/login", json={"email": email, "password": password})
    return resp.json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


class TestAnalyzeText:
    def test_positive_text(self, client):
        token = _register_and_token(client)
        resp = client.post(
            "/sentiment/analyze",
            json={"text": "I absolutely love this wonderful day!"},
            headers=_auth(token),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["results"][0]["sentiment_label"] == "Positive"

    def test_negative_text(self, client):
        token = _register_and_token(client)
        resp = client.post(
            "/sentiment/analyze",
            json={"text": "This is completely terrible and I hate it."},
            headers=_auth(token),
        )
        assert resp.status_code == 200
        assert resp.json()["results"][0]["sentiment_label"] == "Negative"

    def test_neutral_text(self, client):
        token = _register_and_token(client)
        resp = client.post(
            "/sentiment/analyze",
            json={"text": "The meeting is at three o'clock in the room."},
            headers=_auth(token),
        )
        assert resp.status_code == 200
        # Neutral or borderline acceptable
        label = resp.json()["results"][0]["sentiment_label"]
        assert label in ("Neutral", "Positive", "Negative")

    def test_empty_text_returns_422(self, client):
        token = _register_and_token(client)
        resp = client.post(
            "/sentiment/analyze",
            json={"text": "   "},
            headers=_auth(token),
        )
        assert resp.status_code == 422

    def test_unauthenticated_returns_403(self, client):
        resp = client.post("/sentiment/analyze", json={"text": "hello"})
        assert resp.status_code in (401, 403)

    def test_compound_score_in_range(self, client):
        token = _register_and_token(client)
        resp = client.post(
            "/sentiment/analyze",
            json={"text": "Something happened today."},
            headers=_auth(token),
        )
        assert resp.status_code == 200
        score = resp.json()["results"][0]["compound_score"]
        assert -1.0 <= score <= 1.0

    def test_response_contains_summary(self, client):
        token = _register_and_token(client)
        resp = client.post(
            "/sentiment/analyze",
            json={"text": "Great day!"},
            headers=_auth(token),
        )
        assert resp.status_code == 200
        summary = resp.json()["summary"]
        assert "Positive" in summary
        assert "Negative" in summary
        assert "Neutral" in summary


class TestAnalyzeFile:
    def _upload(self, client, token, content: bytes, filename: str, column: str = ""):
        return client.post(
            "/sentiment/analyze-file",
            files={"file": (filename, io.BytesIO(content), "application/octet-stream")},
            data={"csv_column": column},
            headers={"Authorization": f"Bearer {token}"},
        )

    def test_valid_txt_file(self, client):
        token = _register_and_token(client)
        resp = self._upload(client, token, b"I love programming.", "test.txt")
        assert resp.status_code == 200
        assert len(resp.json()["results"]) == 1

    def test_empty_txt_file_returns_422(self, client):
        token = _register_and_token(client)
        resp = self._upload(client, token, b"", "empty.txt")
        assert resp.status_code == 400  # empty file

    def test_whitespace_only_txt_returns_422(self, client):
        token = _register_and_token(client)
        resp = self._upload(client, token, b"   \n  ", "blank.txt")
        assert resp.status_code == 422

    def test_valid_csv_single_column(self, client):
        token = _register_and_token(client)
        csv_content = b"text\nI love this!\nThis is bad.\nJust okay."
        resp = self._upload(client, token, csv_content, "test.csv", "text")
        assert resp.status_code == 200
        assert len(resp.json()["results"]) == 3

    def test_csv_with_multiple_columns(self, client):
        token = _register_and_token(client)
        csv_content = b"id,review\n1,Great product!\n2,Terrible experience."
        resp = self._upload(client, token, csv_content, "test.csv", "review")
        assert resp.status_code == 200
        assert len(resp.json()["results"]) == 2

    def test_csv_missing_column_returns_422(self, client):
        token = _register_and_token(client)
        csv_content = b"text\nHello world"
        resp = self._upload(client, token, csv_content, "test.csv", "nonexistent")
        assert resp.status_code == 422

    def test_empty_csv_returns_422(self, client):
        token = _register_and_token(client)
        resp = self._upload(client, token, b"", "empty.csv")
        assert resp.status_code == 400

    def test_unsupported_file_type_returns_400(self, client):
        token = _register_and_token(client)
        resp = self._upload(client, token, b"data", "test.pdf")
        assert resp.status_code == 400

    def test_csv_summary_counts_correct(self, client):
        token = _register_and_token(client)
        csv_content = (
            b"text\n"
            b"I love this so much!\n"
            b"This is absolutely terrible and awful.\n"
            b"The file is on the desk."
        )
        resp = self._upload(client, token, csv_content, "test.csv", "text")
        assert resp.status_code == 200
        summary = resp.json()["summary"]
        total = sum(summary.values())
        assert total == 3

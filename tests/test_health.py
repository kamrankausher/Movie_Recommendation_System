"""Tests for the /health endpoint."""


def test_health_returns_200(client):
    """Health endpoint should return 200 with status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_response_format(client):
    """Health response should be valid JSON with expected keys."""
    response = client.get("/health")
    data = response.json()
    assert "status" in data
    assert isinstance(data["status"], str)

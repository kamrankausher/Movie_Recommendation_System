"""Tests for the home and general API endpoints.

Note: Endpoints that call the external TMDB API may return 502
if TMDB is unreachable (e.g., in CI or offline environments).
These tests accept both 200 (online) and 502 (offline) responses.
"""

import pytest


def test_home_default_category(client):
    """Home endpoint should return a list of movie cards (or 502 if TMDB unreachable)."""
    response = client.get("/home")
    assert response.status_code in (200, 502)
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)


def test_home_invalid_category(client):
    """Should return 400 for an invalid category."""
    response = client.get("/home", params={"category": "invalid_category"})
    assert response.status_code == 400


def test_home_limit_parameter(client):
    """Should respect the limit parameter when TMDB is reachable."""
    response = client.get("/home", params={"limit": 5})
    assert response.status_code in (200, 502)
    if response.status_code == 200:
        data = response.json()
        assert len(data) <= 5


def test_home_limit_validation_zero(client):
    """Should reject limit=0 (below minimum)."""
    response = client.get("/home", params={"limit": 0})
    assert response.status_code == 422


def test_home_limit_validation_too_high(client):
    """Should reject limit=100 (above maximum)."""
    response = client.get("/home", params={"limit": 100})
    assert response.status_code == 422


def test_tmdb_search_valid_query(client):
    """TMDB search should return results for a valid query (or 502 offline)."""
    response = client.get("/tmdb/search", params={"query": "Avatar"})
    assert response.status_code in (200, 502)
    if response.status_code == 200:
        data = response.json()
        assert "results" in data


def test_tmdb_search_empty_query(client):
    """Should return 422 for an empty search query."""
    response = client.get("/tmdb/search", params={"query": ""})
    assert response.status_code == 422


def test_tmdb_search_missing_query(client):
    """Should return 422 when query parameter is missing."""
    response = client.get("/tmdb/search")
    assert response.status_code == 422


def test_movie_card_format(client):
    """Home endpoint cards should have expected fields when TMDB is reachable."""
    response = client.get("/home", params={"limit": 1})
    if response.status_code == 200 and response.json():
        card = response.json()[0]
        assert "tmdb_id" in card
        assert "title" in card
        assert isinstance(card["tmdb_id"], int)
        assert isinstance(card["title"], str)

"""Tests for the TF-IDF recommendation endpoint."""


def test_tfidf_valid_title(client):
    """Should return recommendations for a known movie title."""
    response = client.get("/recommend/tfidf", params={"title": "Toy Story"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Each item should have title and score
    for item in data:
        assert "title" in item
        assert "score" in item
        assert isinstance(item["score"], float)


def test_tfidf_default_returns_10(client):
    """Should return 10 recommendations by default."""
    response = client.get("/recommend/tfidf", params={"title": "Jumanji"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10


def test_tfidf_custom_top_n(client):
    """Should respect the top_n parameter."""
    response = client.get(
        "/recommend/tfidf", params={"title": "Toy Story", "top_n": 5}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5


def test_tfidf_unknown_title_returns_404(client):
    """Should return 404 for a title not in the local dataset."""
    response = client.get(
        "/recommend/tfidf",
        params={"title": "ThisMovieDoesNotExist12345"},
    )
    assert response.status_code == 404


def test_tfidf_empty_title_returns_422(client):
    """Should return 422 for an empty title (validation error)."""
    response = client.get("/recommend/tfidf", params={"title": ""})
    assert response.status_code == 422


def test_tfidf_missing_title_returns_422(client):
    """Should return 422 when title parameter is missing."""
    response = client.get("/recommend/tfidf")
    assert response.status_code == 422


def test_tfidf_scores_are_sorted_descending(client):
    """Recommendation scores should be in descending order."""
    response = client.get("/recommend/tfidf", params={"title": "Batman"})
    if response.status_code == 200:
        data = response.json()
        scores = [item["score"] for item in data]
        assert scores == sorted(scores, reverse=True)


def test_tfidf_does_not_return_self(client):
    """The query movie itself should not appear in recommendations."""
    title = "Toy Story"
    response = client.get("/recommend/tfidf", params={"title": title})
    assert response.status_code == 200
    data = response.json()
    recommended_titles = [item["title"].lower() for item in data]
    assert title.lower() not in recommended_titles

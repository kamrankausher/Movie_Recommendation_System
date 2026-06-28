"""Recommendation endpoints — TF-IDF and genre-based."""

import logging
from typing import List

from fastapi import APIRouter, HTTPException, Query

from app.models import TMDBMovieCard
from app.services.tmdb import get_movie_details, tmdb_get, tmdb_cards_from_results
from app.services.recommender import recommend_by_title

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/recommend/tfidf")
async def recommend_tfidf(
    title: str = Query(..., min_length=1),
    top_n: int = Query(10, ge=1, le=50),
):
    """Get TF-IDF content-based recommendations for a movie.

    Uses cosine similarity on the precomputed TF-IDF sparse matrix
    to find the most similar movies based on text features
    (overview, genres, tagline).

    Args:
        title: Movie title to find recommendations for.
        top_n: Number of recommendations (1–50).

    Returns:
        List of {title, score} objects sorted by similarity.
    """
    recs = recommend_by_title(title, top_n=top_n)
    return [{"title": t, "score": s} for t, s in recs]


@router.get("/recommend/genre", response_model=List[TMDBMovieCard])
async def recommend_genre(
    tmdb_id: int = Query(...),
    limit: int = Query(18, ge=1, le=50),
):
    """Get genre-based recommendations from TMDB Discover.

    Fetches the movie's details, takes its primary genre,
    and queries TMDB Discover for popular movies in that genre.

    Args:
        tmdb_id: The TMDB movie ID.
        limit: Maximum recommendations to return (1–50).

    Returns:
        List of TMDBMovieCard objects (excluding the original movie).
    """
    details = await get_movie_details(tmdb_id)
    if not details.genres:
        return []

    genre_id = details.genres[0]["id"]
    discover = await tmdb_get(
        "/discover/movie",
        {
            "with_genres": genre_id,
            "language": "en-US",
            "sort_by": "popularity.desc",
            "page": 1,
        },
    )
    cards = await tmdb_cards_from_results(discover.get("results", []), limit=limit)
    return [c for c in cards if c.tmdb_id != tmdb_id]

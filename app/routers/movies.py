"""Movie details and search bundle endpoints."""

import logging
from typing import List, Tuple

from fastapi import APIRouter, HTTPException, Query

from app.models import (
    TMDBMovieCard,
    TMDBMovieDetails,
    TFIDFRecItem,
    SearchBundleResponse,
)
from app.services.tmdb import (
    get_movie_details,
    search_first_movie,
    tmdb_get,
    tmdb_cards_from_results,
    get_card_by_title,
)
from app.services.recommender import recommend_by_title

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/movie/id/{tmdb_id}", response_model=TMDBMovieDetails)
async def movie_details_by_id(tmdb_id: int):
    """Get full details for a movie by its TMDB ID.

    Args:
        tmdb_id: The TMDB movie ID.

    Returns:
        TMDBMovieDetails with poster, backdrop, genres, overview, etc.
    """
    return await get_movie_details(tmdb_id)


@router.get("/movie/search", response_model=SearchBundleResponse)
async def search_bundle(
    query: str = Query(..., min_length=1),
    tfidf_top_n: int = Query(12, ge=1, le=30),
    genre_limit: int = Query(12, ge=1, le=30),
):
    """Search for a movie and get a combined recommendation bundle.

    This endpoint returns:
    - Movie details from TMDB
    - TF-IDF content-based recommendations (from the local dataset)
    - Genre-based recommendations (from TMDB Discover)

    Args:
        query: Movie title to search for.
        tfidf_top_n: Number of TF-IDF recommendations (1–30).
        genre_limit: Number of genre recommendations (1–30).

    Returns:
        SearchBundleResponse with all three recommendation types.
    """
    best = await search_first_movie(query)
    if not best:
        raise HTTPException(
            status_code=404,
            detail=f"No TMDB movie found for query: {query}",
        )

    tmdb_id = int(best["id"])
    details = await get_movie_details(tmdb_id)

    # --- TF-IDF recommendations (graceful fallback) ---
    tfidf_items: List[TFIDFRecItem] = []
    recs: List[Tuple[str, float]] = []

    try:
        recs = recommend_by_title(details.title, top_n=tfidf_top_n)
    except Exception:
        try:
            recs = recommend_by_title(query, top_n=tfidf_top_n)
        except Exception:
            logger.warning("TF-IDF recommendations unavailable for '%s'", query)
            recs = []

    for title, score in recs:
        card = await get_card_by_title(title)
        tfidf_items.append(TFIDFRecItem(title=title, score=score, tmdb=card))

    # --- Genre recommendations (TMDB Discover) ---
    genre_recs: List[TMDBMovieCard] = []
    if details.genres:
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
        cards = await tmdb_cards_from_results(
            discover.get("results", []), limit=genre_limit
        )
        genre_recs = [c for c in cards if c.tmdb_id != details.tmdb_id]

    return SearchBundleResponse(
        query=query,
        movie_details=details,
        tfidf_recommendations=tfidf_items,
        genre_recommendations=genre_recs,
    )

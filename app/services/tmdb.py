"""
TMDB API service module.

Handles all communication with The Movie Database (TMDB) API,
including search, details, and discover endpoints.
"""

import logging
from typing import Optional, List, Dict, Any

import httpx
from fastapi import HTTPException

from app.config import TMDB_API_KEY, TMDB_BASE_URL, TMDB_REQUEST_TIMEOUT
from app.models import TMDBMovieCard, TMDBMovieDetails
from app.utils.helpers import make_image_url

logger = logging.getLogger(__name__)


async def tmdb_get(path: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Make a GET request to the TMDB API.

    Args:
        path: API endpoint path (e.g., '/movie/123').
        params: Query parameters to include.

    Returns:
        Parsed JSON response from TMDB.

    Raises:
        HTTPException: On network errors or non-200 TMDB responses.
    """
    query = dict(params)
    query["api_key"] = TMDB_API_KEY

    try:
        async with httpx.AsyncClient(timeout=TMDB_REQUEST_TIMEOUT) as client:
            response = await client.get(f"{TMDB_BASE_URL}{path}", params=query)
    except httpx.RequestError as exc:
        logger.error("TMDB request failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail=f"TMDB request error: {type(exc).__name__}",
        )

    if response.status_code != 200:
        logger.warning("TMDB returned %d: %s", response.status_code, response.text)
        raise HTTPException(
            status_code=502,
            detail=f"TMDB error {response.status_code}: {response.text}",
        )

    return response.json()


async def tmdb_cards_from_results(
    results: List[dict], limit: int = 20
) -> List[TMDBMovieCard]:
    """Convert raw TMDB search results into TMDBMovieCard objects.

    Args:
        results: List of raw movie dicts from TMDB API.
        limit: Maximum number of cards to return.

    Returns:
        List of TMDBMovieCard objects.
    """
    cards: List[TMDBMovieCard] = []
    for movie in (results or [])[:limit]:
        cards.append(
            TMDBMovieCard(
                tmdb_id=int(movie["id"]),
                title=movie.get("title") or movie.get("name") or "",
                poster_url=make_image_url(movie.get("poster_path")),
                release_date=movie.get("release_date"),
                vote_average=movie.get("vote_average"),
            )
        )
    return cards


async def get_movie_details(movie_id: int) -> TMDBMovieDetails:
    """Fetch full details for a single movie from TMDB.

    Args:
        movie_id: The TMDB movie ID.

    Returns:
        TMDBMovieDetails with poster, backdrop, genres, etc.
    """
    data = await tmdb_get(f"/movie/{movie_id}", {"language": "en-US"})
    return TMDBMovieDetails(
        tmdb_id=int(data["id"]),
        title=data.get("title") or "",
        overview=data.get("overview"),
        release_date=data.get("release_date"),
        poster_url=make_image_url(data.get("poster_path")),
        backdrop_url=make_image_url(data.get("backdrop_path")),
        genres=data.get("genres", []) or [],
    )


async def search_movies(query: str, page: int = 1) -> Dict[str, Any]:
    """Search TMDB for movies matching a keyword query.

    Args:
        query: Search keyword(s).
        page: Result page number (1-indexed).

    Returns:
        Raw TMDB response with 'results' list.
    """
    return await tmdb_get(
        "/search/movie",
        {
            "query": query,
            "include_adult": "false",
            "language": "en-US",
            "page": page,
        },
    )


async def search_first_movie(query: str) -> Optional[dict]:
    """Search TMDB and return only the first (best) match.

    Args:
        query: Search keyword(s).

    Returns:
        First movie result dict, or None if no results.
    """
    data = await search_movies(query=query, page=1)
    results = data.get("results", [])
    return results[0] if results else None


async def get_card_by_title(title: str) -> Optional[TMDBMovieCard]:
    """Search TMDB by title and return a movie card.

    Used to attach poster images to local TF-IDF recommendations.
    Never raises exceptions — returns None on any failure.

    Args:
        title: Movie title to search for.

    Returns:
        TMDBMovieCard or None.
    """
    try:
        movie = await search_first_movie(title)
        if not movie:
            return None
        return TMDBMovieCard(
            tmdb_id=int(movie["id"]),
            title=movie.get("title") or title,
            poster_url=make_image_url(movie.get("poster_path")),
            release_date=movie.get("release_date"),
            vote_average=movie.get("vote_average"),
        )
    except Exception as exc:
        logger.debug("Failed to fetch TMDB card for '%s': %s", title, exc)
        return None

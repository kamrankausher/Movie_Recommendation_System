"""Home feed endpoint — provides movie cards for the landing page."""

import logging
from typing import List

from fastapi import APIRouter, HTTPException, Query

from app.models import TMDBMovieCard
from app.services.tmdb import tmdb_get, tmdb_cards_from_results

logger = logging.getLogger(__name__)
router = APIRouter()

VALID_CATEGORIES = {"popular", "top_rated", "upcoming", "now_playing"}


@router.get("/home", response_model=List[TMDBMovieCard])
async def home_feed(
    category: str = Query("popular"),
    limit: int = Query(24, ge=1, le=50),
):
    """Get a list of movie cards for the home page.

    Args:
        category: One of 'trending', 'popular', 'top_rated',
                  'upcoming', or 'now_playing'.
        limit: Maximum number of movies to return (1–50).

    Returns:
        List of TMDBMovieCard objects with poster URLs.
    """
    try:
        if category == "trending":
            data = await tmdb_get("/trending/movie/day", {"language": "en-US"})
            return await tmdb_cards_from_results(data.get("results", []), limit=limit)

        if category not in VALID_CATEGORIES:
            raise HTTPException(status_code=400, detail="Invalid category")

        data = await tmdb_get(
            f"/movie/{category}", {"language": "en-US", "page": 1}
        )
        return await tmdb_cards_from_results(data.get("results", []), limit=limit)

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Home feed failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Home route failed: {exc}")

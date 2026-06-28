"""TMDB search endpoint — keyword search returning multiple results."""

from fastapi import APIRouter, Query

from app.services.tmdb import search_movies

router = APIRouter()


@router.get("/tmdb/search")
async def tmdb_search(
    query: str = Query(..., min_length=1),
    page: int = Query(1, ge=1, le=10),
):
    """Search TMDB for movies matching a keyword.

    Returns the raw TMDB response with a 'results' list,
    used by the Streamlit frontend for search suggestions and grid display.

    Args:
        query: Search keyword(s).
        page: Result page number (1–10).

    Returns:
        Raw TMDB JSON response with 'results', 'total_results', etc.
    """
    return await search_movies(query=query, page=page)

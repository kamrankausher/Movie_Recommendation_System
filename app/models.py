"""
Pydantic models for API request/response schemas.

These models define the shape of data returned by the API endpoints,
ensuring consistent and validated JSON responses.
"""

from typing import Optional, List
from pydantic import BaseModel


class TMDBMovieCard(BaseModel):
    """Compact movie card used in grid/list views."""

    tmdb_id: int
    title: str
    poster_url: Optional[str] = None
    release_date: Optional[str] = None
    vote_average: Optional[float] = None


class TMDBMovieDetails(BaseModel):
    """Full movie details returned for a single movie view."""

    tmdb_id: int
    title: str
    overview: Optional[str] = None
    release_date: Optional[str] = None
    poster_url: Optional[str] = None
    backdrop_url: Optional[str] = None
    genres: List[dict] = []


class TFIDFRecItem(BaseModel):
    """A single TF-IDF recommendation with similarity score."""

    title: str
    score: float
    tmdb: Optional[TMDBMovieCard] = None


class SearchBundleResponse(BaseModel):
    """Combined response with movie details + both recommendation types."""

    query: str
    movie_details: TMDBMovieDetails
    tfidf_recommendations: List[TFIDFRecItem]
    genre_recommendations: List[TMDBMovieCard]

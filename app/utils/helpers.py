"""
Shared utility functions used across the application.
"""

from typing import Optional
from app.config import TMDB_IMAGE_BASE


def normalize_title(title: str) -> str:
    """Normalize a movie title for case-insensitive lookup."""
    return str(title).strip().lower()


def make_image_url(path: Optional[str]) -> Optional[str]:
    """Convert a TMDB image path to a full URL.

    Args:
        path: The TMDB image path (e.g., '/abc123.jpg').

    Returns:
        Full image URL or None if path is empty.
    """
    if not path:
        return None
    return f"{TMDB_IMAGE_BASE}{path}"

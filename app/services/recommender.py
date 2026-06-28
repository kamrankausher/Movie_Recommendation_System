"""
TF-IDF based movie recommendation service.

Loads precomputed TF-IDF sparse matrix and provides
content-based movie recommendations using cosine similarity.
"""

import logging
import pickle
from typing import Optional, Dict, List, Tuple, Any

import numpy as np
import pandas as pd
from fastapi import HTTPException

from app.config import DF_PATH, INDICES_PATH, TFIDF_MATRIX_PATH, TFIDF_VECTORIZER_PATH
from app.utils.helpers import normalize_title

logger = logging.getLogger(__name__)

# --- Module-level state (loaded once at startup) ---
df: Optional[pd.DataFrame] = None
tfidf_matrix: Any = None
tfidf_vectorizer: Any = None
TITLE_TO_IDX: Optional[Dict[str, int]] = None


def _build_title_index(indices: Any) -> Dict[str, int]:
    """Build a normalized title-to-row-index mapping.

    Args:
        indices: A dict or Pandas Series mapping titles to row indices.

    Returns:
        Dictionary with lowercase titles as keys and row indices as values.

    Raises:
        RuntimeError: If the indices format is not supported.
    """
    title_to_idx: Dict[str, int] = {}

    if isinstance(indices, dict):
        for key, value in indices.items():
            title_to_idx[normalize_title(key)] = int(value)
        return title_to_idx

    # Handle Pandas Series or similar mapping
    try:
        for key, value in indices.items():
            title_to_idx[normalize_title(key)] = int(value)
        return title_to_idx
    except Exception as exc:
        raise RuntimeError(
            "indices.pkl must be a dict or Pandas Series with .items()"
        ) from exc


def load_data() -> None:
    """Load all pickle files into module-level variables.

    Called once during application startup. Loads the DataFrame,
    TF-IDF matrix, vectorizer, and builds the title index.

    Raises:
        RuntimeError: If required files are missing or malformed.
    """
    global df, tfidf_matrix, tfidf_vectorizer, TITLE_TO_IDX

    logger.info("Loading data files...")

    with open(DF_PATH, "rb") as f:
        df = pickle.load(f)

    with open(INDICES_PATH, "rb") as f:
        indices = pickle.load(f)

    with open(TFIDF_MATRIX_PATH, "rb") as f:
        tfidf_matrix = pickle.load(f)

    with open(TFIDF_VECTORIZER_PATH, "rb") as f:
        tfidf_vectorizer = pickle.load(f)

    TITLE_TO_IDX = _build_title_index(indices)

    if df is None or "title" not in df.columns:
        raise RuntimeError("df.pkl must contain a DataFrame with a 'title' column")

    logger.info(
        "Data loaded: %d movies, TF-IDF matrix shape %s",
        len(df),
        tfidf_matrix.shape,
    )


def get_index_by_title(title: str) -> int:
    """Look up the row index for a movie title.

    Args:
        title: Movie title (case-insensitive).

    Returns:
        Row index in the DataFrame / TF-IDF matrix.

    Raises:
        HTTPException: 500 if data not loaded, 404 if title not found.
    """
    if TITLE_TO_IDX is None:
        raise HTTPException(status_code=500, detail="TF-IDF index not initialized")

    key = normalize_title(title)
    if key in TITLE_TO_IDX:
        return int(TITLE_TO_IDX[key])

    raise HTTPException(
        status_code=404,
        detail=f"Title not found in local dataset: '{title}'",
    )


def recommend_by_title(
    query_title: str, top_n: int = 10
) -> List[Tuple[str, float]]:
    """Get content-based recommendations using TF-IDF cosine similarity.

    Computes similarity between the query movie's TF-IDF vector and all
    other movies, then returns the top-N most similar titles.

    Args:
        query_title: The movie title to find recommendations for.
        top_n: Number of recommendations to return.

    Returns:
        List of (title, similarity_score) tuples, sorted by score descending.

    Raises:
        HTTPException: If data is not loaded or title is not found.
    """
    if df is None or tfidf_matrix is None:
        raise HTTPException(status_code=500, detail="TF-IDF resources not loaded")

    idx = get_index_by_title(query_title)

    # Compute cosine similarity using sparse matrix multiplication
    query_vector = tfidf_matrix[idx]
    scores = (tfidf_matrix @ query_vector.T).toarray().ravel()

    # Sort by score descending
    ranked_indices = np.argsort(-scores)

    results: List[Tuple[str, float]] = []
    for i in ranked_indices:
        if int(i) == int(idx):
            continue
        try:
            title = str(df.iloc[int(i)]["title"])
        except (IndexError, KeyError):
            continue
        results.append((title, float(scores[int(i)])))
        if len(results) >= top_n:
            break

    return results

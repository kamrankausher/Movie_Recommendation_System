"""
Application configuration module.

Loads environment variables and defines constants used across the application.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# --- TMDB API ---
TMDB_API_KEY: str = os.getenv("TMDB_API_KEY", "")
TMDB_BASE_URL: str = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE: str = "https://image.tmdb.org/t/p/w500"

# --- Data File Paths ---
BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR: str = os.path.join(BASE_DIR, "data")
DF_PATH: str = os.path.join(DATA_DIR, "df.pkl")
INDICES_PATH: str = os.path.join(DATA_DIR, "indices.pkl")
TFIDF_MATRIX_PATH: str = os.path.join(DATA_DIR, "tfidf_matrix.pkl")
TFIDF_VECTORIZER_PATH: str = os.path.join(DATA_DIR, "tfidf.pkl")

# --- Server ---
TMDB_REQUEST_TIMEOUT: int = 20
CORS_ORIGINS: list = ["*"]

# --- Validation ---
if not TMDB_API_KEY:
    raise RuntimeError(
        "TMDB_API_KEY missing. Create a .env file with TMDB_API_KEY=your_key"
    )

"""
FastAPI application factory.

Creates the FastAPI app, registers middleware, includes routers,
and loads data files on startup using the lifespan context manager.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS
from app.services.recommender import load_data
from app.routers import health, home, search, movies, recommend

# --- Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Load data files on startup, clean up on shutdown."""
    logger.info("Starting up — loading data files...")
    load_data()
    logger.info("Data loaded successfully.")
    yield
    logger.info("Shutting down.")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI app with all routers and middleware.
    """
    application = FastAPI(
        title="Movie Recommender API",
        version="3.0",
        description="Content-based movie recommendation system using TF-IDF.",
        lifespan=lifespan,
    )

    # --- CORS Middleware ---
    application.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Register Routers ---
    application.include_router(health.router)
    application.include_router(home.router)
    application.include_router(search.router)
    application.include_router(movies.router)
    application.include_router(recommend.router)

    return application


# Module-level app instance used by uvicorn
app = create_app()

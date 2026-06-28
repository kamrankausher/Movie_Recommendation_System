"""Health check endpoint."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    """Return server health status.

    Used by Render and monitoring tools to verify the API is running.
    """
    return {"status": "ok"}

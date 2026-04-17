"""Backend API routers."""

from app.routers.auth import router as auth_router
from app.routers.assets import router as assets_router
from app.routers.etl import router as etl_router
from app.routers.health import router as health_router

__all__ = ["auth_router", "assets_router", "etl_router", "health_router"]

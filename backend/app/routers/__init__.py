"""Backend API routers."""

from app.routers.ai import router as ai_router
from app.routers.alerts import router as alerts_router
from app.routers.auth import router as auth_router
from app.routers.assets import router as assets_router
from app.routers.etl import router as etl_router
from app.routers.health import router as health_router
from app.routers.portfolios import router as portfolios_router
from app.routers.risk_indicators import router as risk_indicators_router
from app.routers.trades import router as trades_router

__all__ = [
    "ai_router",
    "alerts_router",
    "auth_router",
    "assets_router",
    "etl_router",
    "health_router",
    "portfolios_router",
    "risk_indicators_router",
    "trades_router",
]

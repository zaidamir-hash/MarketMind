from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routers.ai import router as ai_router
from app.routers.alerts import router as alerts_router
from app.routers.auth import router as auth_router
from app.routers.assets import router as assets_router
from app.routers.etl import router as etl_router
from app.routers.health import router as health_router
from app.routers.portfolios import router as portfolios_router
from app.routers.risk_indicators import router as risk_indicators_router
from app.routers.trades import router as trades_router


settings = get_settings()

app = FastAPI(
    title="MarketMind API",
    version="0.1.0",
    description="FastAPI backend foundation for the MarketMind project.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["root"])
def read_root() -> dict[str, str]:
    return {
        "message": "MarketMind API is running.",
        "version": app.version,
    }


app.include_router(health_router)
app.include_router(auth_router)
app.include_router(assets_router)
app.include_router(etl_router)
app.include_router(risk_indicators_router)
app.include_router(ai_router)
app.include_router(portfolios_router)
app.include_router(trades_router)
app.include_router(alerts_router)

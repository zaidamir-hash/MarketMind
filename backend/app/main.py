from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routers.auth import router as auth_router
from app.routers.health import router as health_router


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

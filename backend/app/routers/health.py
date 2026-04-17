from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import get_db


router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "MarketMind API",
    }


@router.get("/health/db")
def database_health_check(db: Session = Depends(get_db)) -> dict[str, object]:
    try:
        db.execute(text("SELECT 1")).scalar_one()
        schema_exists = db.execute(
            text(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.schemata
                    WHERE schema_name = 'marketmind'
                )
                """
            )
        ).scalar_one()
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "error",
                "database": "unavailable",
                "message": str(exc.__class__.__name__),
            },
        ) from exc

    if not schema_exists:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "error",
                "database": "connected",
                "schema": "marketmind",
                "schema_exists": False,
            },
        )

    return {
        "status": "ok",
        "database": "connected",
        "schema": "marketmind",
        "schema_exists": True,
    }

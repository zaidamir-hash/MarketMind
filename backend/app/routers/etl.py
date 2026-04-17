from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.session import get_db
from app.dependencies.auth import get_current_active_user
from app.schemas.asset import AssetRead
from app.schemas.etl import (
    ETLBatchItem,
    ETLBatchResponse,
    ETLJobResponse,
    FetchPricesRequest,
    OnboardAssetRequest,
    ScraperLogRead,
)
from app.services.yfinance_etl_service import (
    fetch_prices_for_all_active_assets,
    fetch_prices_for_asset,
    list_recent_scraper_logs,
    onboard_asset_from_yfinance,
)


router = APIRouter(prefix="/etl", tags=["ETL"])


@router.post("/onboard-asset", response_model=ETLJobResponse)
def onboard_asset(
    request: OnboardAssetRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ETLJobResponse:
    _ = current_user
    try:
        asset = onboard_asset_from_yfinance(db, request.symbol)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return ETLJobResponse(
        status="SUCCESS",
        message="Asset onboarded from yfinance.",
        symbol=asset.symbol,
        rows_inserted=1,
        asset=AssetRead.model_validate(asset),
    )


@router.post("/fetch-prices", response_model=ETLJobResponse)
def fetch_prices(
    request: FetchPricesRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ETLJobResponse:
    _ = current_user
    if not request.symbol:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="symbol is required for /etl/fetch-prices.",
        )

    try:
        rows_inserted = fetch_prices_for_asset(
            db,
            request.symbol,
            period=request.period,
            interval=request.interval,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return ETLJobResponse(
        status="SUCCESS",
        message="Price history fetched successfully.",
        symbol=request.symbol,
        rows_inserted=rows_inserted,
    )


@router.post("/fetch-prices/all-active", response_model=ETLBatchResponse)
def fetch_prices_all_active(
    request: FetchPricesRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ETLBatchResponse:
    _ = current_user
    summary = fetch_prices_for_all_active_assets(
        db,
        period=request.period,
        interval=request.interval,
    )
    items = [ETLBatchItem(**item) for item in summary]
    overall_status = "SUCCESS" if all(item.status == "SUCCESS" for item in items) else "PARTIAL"
    return ETLBatchResponse(
        status=overall_status,
        message="Fetched prices for all active assets.",
        details=items,
    )


@router.get("/logs", response_model=list[ScraperLogRead])
def read_scraper_logs(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[ScraperLogRead]:
    _ = current_user
    logs = list_recent_scraper_logs(db, limit=limit)
    return [ScraperLogRead.model_validate(log) for log in logs]

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.session import get_db
from app.dependencies.auth import get_current_active_user
from app.schemas.risk_indicator import (
    RiskIndicatorBatchItem,
    RiskIndicatorBatchResponse,
    RiskIndicatorComputeRequest,
    RiskIndicatorComputeResponse,
    RiskIndicatorRead,
)
from app.services.risk_indicator_service import (
    compute_risk_indicators_for_all_active_assets,
    compute_risk_indicators_for_asset,
    get_latest_risk_indicator_for_asset,
    list_latest_risk_indicators,
)


router = APIRouter(prefix="/risk-indicators", tags=["Risk Indicators"])


def _to_risk_indicator_read(risk_indicator: object, symbol: str | None = None) -> RiskIndicatorRead:
    payload = RiskIndicatorRead.model_validate(risk_indicator).model_dump()
    payload["symbol"] = symbol
    return RiskIndicatorRead(**payload)


@router.post("/compute", response_model=RiskIndicatorComputeResponse)
def compute_risk_indicator(
    request: RiskIndicatorComputeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> RiskIndicatorComputeResponse:
    _ = current_user
    try:
        indicator = compute_risk_indicators_for_asset(db, request.symbol)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    return RiskIndicatorComputeResponse(
        status="SUCCESS",
        message="Risk indicators computed successfully.",
        symbol=request.symbol,
        risk_indicator=_to_risk_indicator_read(indicator, symbol=request.symbol),
    )


@router.post("/compute/all-active", response_model=RiskIndicatorBatchResponse)
def compute_risk_indicators_batch(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> RiskIndicatorBatchResponse:
    _ = current_user
    summary = compute_risk_indicators_for_all_active_assets(db)
    items = [RiskIndicatorBatchItem(**item) for item in summary]
    overall_status = "SUCCESS" if all(item.status == "SUCCESS" for item in items) else "PARTIAL"
    return RiskIndicatorBatchResponse(
        status=overall_status,
        message="Computed risk indicators for active assets.",
        details=items,
    )


@router.get("", response_model=list[RiskIndicatorRead])
def read_latest_risk_indicators(
    active_only: bool = Query(default=True),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[RiskIndicatorRead]:
    rows = list_latest_risk_indicators(db, active_only=active_only, limit=limit)
    return [_to_risk_indicator_read(risk_indicator, symbol) for risk_indicator, symbol in rows]


@router.get("/symbol/{symbol}", response_model=RiskIndicatorRead)
def read_latest_risk_indicator_for_symbol(
    symbol: str,
    db: Session = Depends(get_db),
) -> RiskIndicatorRead:
    row = get_latest_risk_indicator_for_asset(db, symbol)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No risk indicators found for asset '{symbol.strip().upper()}'.",
        )

    risk_indicator, asset_symbol = row
    return _to_risk_indicator_read(risk_indicator, asset_symbol)

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.session import get_db
from app.dependencies.auth import get_current_active_user
from app.schemas.ai import (
    AIBatchItem,
    AIBatchResponse,
    AIPipelineResponse,
    HMMStateRead,
    PredictionRead,
    SignalRead,
)
from app.schemas.risk_indicator import RiskIndicatorRead
from app.services.ai_service import (
    get_latest_prediction_for_asset,
    get_latest_regime_for_asset,
    get_latest_signal_for_asset,
    list_latest_predictions,
    list_latest_regimes,
    list_latest_signals,
    run_ai_pipeline_for_all_active_assets,
    run_ai_pipeline_for_asset,
)


router = APIRouter(prefix="/ai", tags=["AI"])


def _to_prediction_read(prediction: object, symbol: str | None = None) -> PredictionRead:
    payload = PredictionRead.model_validate(prediction).model_dump()
    payload["symbol"] = symbol
    return PredictionRead(**payload)


def _to_signal_read(signal: object, symbol: str | None = None) -> SignalRead:
    payload = SignalRead.model_validate(signal).model_dump()
    payload["symbol"] = symbol
    return SignalRead(**payload)


def _to_regime_read(regime: object, symbol: str | None = None) -> HMMStateRead:
    payload = HMMStateRead.model_validate(regime).model_dump()
    payload["symbol"] = symbol
    return HMMStateRead(**payload)


def _to_risk_read(risk_indicator: object, symbol: str | None = None) -> RiskIndicatorRead:
    payload = RiskIndicatorRead.model_validate(risk_indicator).model_dump()
    payload["symbol"] = symbol
    return RiskIndicatorRead(**payload)


@router.post("/run/{symbol}", response_model=AIPipelineResponse)
def run_ai_pipeline(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AIPipelineResponse:
    _ = current_user
    try:
        result = run_ai_pipeline_for_asset(db, symbol)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    return AIPipelineResponse(
        status=result["status"],
        message=result["message"],
        symbol=result["symbol"],
        regime=_to_regime_read(result["regime"], result["symbol"]),
        prediction=_to_prediction_read(result["prediction"], result["symbol"]),
        risk_indicator=_to_risk_read(result["risk_indicator"], result["symbol"]),
        signal=_to_signal_read(result["signal"], result["symbol"]),
    )


@router.post("/run-all", response_model=AIBatchResponse)
def run_ai_pipeline_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AIBatchResponse:
    _ = current_user
    summary = run_ai_pipeline_for_all_active_assets(db)
    items = [AIBatchItem(**item) for item in summary]
    overall_status = "SUCCESS" if all(item.status == "SUCCESS" for item in items) else "PARTIAL"
    return AIBatchResponse(
        status=overall_status,
        message="AI pipeline finished for active assets.",
        details=items,
    )


@router.get("/predictions/symbol/{symbol}", response_model=PredictionRead)
def read_prediction_for_symbol(
    symbol: str,
    db: Session = Depends(get_db),
) -> PredictionRead:
    row = get_latest_prediction_for_asset(db, symbol)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No AI prediction found for asset '{symbol.strip().upper()}'.",
        )
    prediction, asset_symbol = row
    return _to_prediction_read(prediction, asset_symbol)


@router.get("/predictions", response_model=list[PredictionRead])
def read_predictions(
    active_only: bool = Query(default=True),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[PredictionRead]:
    rows = list_latest_predictions(db, active_only=active_only, limit=limit)
    return [_to_prediction_read(prediction, symbol) for prediction, symbol in rows]


@router.get("/signals/symbol/{symbol}", response_model=SignalRead)
def read_signal_for_symbol(
    symbol: str,
    db: Session = Depends(get_db),
) -> SignalRead:
    row = get_latest_signal_for_asset(db, symbol)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No market signal found for asset '{symbol.strip().upper()}'.",
        )
    signal, asset_symbol = row
    return _to_signal_read(signal, asset_symbol)


@router.get("/signals", response_model=list[SignalRead])
def read_signals(
    active_only: bool = Query(default=True),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[SignalRead]:
    rows = list_latest_signals(db, active_only=active_only, limit=limit)
    return [_to_signal_read(signal, symbol) for signal, symbol in rows]


@router.get("/regimes/symbol/{symbol}", response_model=HMMStateRead)
def read_regime_for_symbol(
    symbol: str,
    db: Session = Depends(get_db),
) -> HMMStateRead:
    row = get_latest_regime_for_asset(db, symbol)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No HMM regime found for asset '{symbol.strip().upper()}'.",
        )
    regime, asset_symbol = row
    return _to_regime_read(regime, asset_symbol)


@router.get("/regimes", response_model=list[HMMStateRead])
def read_regimes(
    active_only: bool = Query(default=True),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[HMMStateRead]:
    rows = list_latest_regimes(db, active_only=active_only, limit=limit)
    return [_to_regime_read(regime, symbol) for regime, symbol in rows]

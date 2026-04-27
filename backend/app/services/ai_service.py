from __future__ import annotations

from sqlalchemy import case, desc, select
from sqlalchemy.orm import Session

from app.ai.bayesian_risk_model import compute_bayesian_risk_for_asset
from app.ai.price_prediction_model import predict_price_for_asset
from app.ai.regime_model import run_regime_detection_for_asset
from app.ai.signal_generator import generate_signal_for_asset
from app.db.models import AIPrediction, Asset, HMMState, MarketSignal
from app.etl.etl_utils import normalize_symbol
from app.services.scraper_log_service import (
    create_scraper_log_start,
    finish_scraper_log_fail,
    finish_scraper_log_success,
)


def run_ai_pipeline_for_asset(db: Session, symbol: str) -> dict[str, object]:
    normalized_symbol = normalize_symbol(symbol)
    log = create_scraper_log_start(db, f"ai_pipeline_{normalized_symbol}")

    try:
        regime = run_regime_detection_for_asset(db, normalized_symbol)
        prediction = predict_price_for_asset(db, normalized_symbol)
        risk_indicator = compute_bayesian_risk_for_asset(db, normalized_symbol)
        signal = generate_signal_for_asset(db, normalized_symbol)
        finish_scraper_log_success(db, log, rows_inserted=4)
        return {
            "status": "SUCCESS",
            "message": "AI pipeline completed successfully.",
            "symbol": normalized_symbol,
            "regime": regime,
            "prediction": prediction,
            "risk_indicator": risk_indicator,
            "signal": signal,
        }
    except Exception as exc:
        finish_scraper_log_fail(db, log, str(exc))
        raise


def run_ai_pipeline_for_all_active_assets(db: Session) -> list[dict[str, object]]:
    active_assets = list(
        db.scalars(
            select(Asset).where(Asset.is_active.is_(True)).order_by(Asset.symbol.asc())
        ).all()
    )

    summary: list[dict[str, object]] = []
    for asset in active_assets:
        try:
            result = run_ai_pipeline_for_asset(db, asset.symbol)
            summary.append(
                {
                    "symbol": asset.symbol,
                    "status": result["status"],
                    "message": result["message"],
                }
            )
        except Exception as exc:
            summary.append(
                {
                    "symbol": asset.symbol,
                    "status": "FAIL",
                    "message": str(exc),
                }
            )
    return summary


def _latest_predictions_query(active_only: bool = True):
    actual_priority = case(
        (AIPrediction.actual_price.is_not(None), 0),
        else_=1,
    )
    ranked_subquery = (
        select(
            AIPrediction.prediction_id.label("prediction_id"),
            AIPrediction.asset_id.label("asset_id"),
            AIPrediction.created_at.label("created_at"),
            Asset.symbol.label("symbol"),
            Asset.is_active.label("is_active"),
            actual_priority.label("actual_priority"),
        )
        .join(Asset, Asset.asset_id == AIPrediction.asset_id)
        .subquery()
    )

    latest_subquery = (
        select(
            ranked_subquery.c.asset_id,
            ranked_subquery.c.symbol,
            ranked_subquery.c.is_active,
            ranked_subquery.c.prediction_id,
            ranked_subquery.c.created_at,
            ranked_subquery.c.actual_priority,
        )
        .distinct(ranked_subquery.c.asset_id)
        .order_by(
            ranked_subquery.c.asset_id,
            ranked_subquery.c.actual_priority.asc(),
            ranked_subquery.c.created_at.desc(),
            ranked_subquery.c.prediction_id.desc(),
        )
        .subquery()
    )

    statement = (
        select(AIPrediction, latest_subquery.c.symbol)
        .join(latest_subquery, latest_subquery.c.prediction_id == AIPrediction.prediction_id)
        .order_by(desc(AIPrediction.created_at), latest_subquery.c.symbol.asc())
    )
    if active_only:
        statement = statement.where(latest_subquery.c.is_active.is_(True))
    return statement


def _latest_signals_query(active_only: bool = True):
    ranked_subquery = (
        select(
            MarketSignal.signal_id.label("signal_id"),
            MarketSignal.asset_id.label("asset_id"),
            MarketSignal.generated_at.label("generated_at"),
            Asset.symbol.label("symbol"),
            Asset.is_active.label("is_active"),
        )
        .join(Asset, Asset.asset_id == MarketSignal.asset_id)
        .subquery()
    )

    latest_subquery = (
        select(
            ranked_subquery.c.asset_id,
            ranked_subquery.c.symbol,
            ranked_subquery.c.is_active,
            ranked_subquery.c.signal_id,
            ranked_subquery.c.generated_at,
        )
        .distinct(ranked_subquery.c.asset_id)
        .order_by(
            ranked_subquery.c.asset_id,
            ranked_subquery.c.generated_at.desc(),
            ranked_subquery.c.signal_id.desc(),
        )
        .subquery()
    )

    statement = (
        select(MarketSignal, latest_subquery.c.symbol)
        .join(latest_subquery, latest_subquery.c.signal_id == MarketSignal.signal_id)
        .order_by(desc(MarketSignal.generated_at), latest_subquery.c.symbol.asc())
    )
    if active_only:
        statement = statement.where(latest_subquery.c.is_active.is_(True))
    return statement


def _latest_regimes_query(active_only: bool = True):
    ranked_subquery = (
        select(
            HMMState.hmm_state_id.label("hmm_state_id"),
            HMMState.asset_id.label("asset_id"),
            HMMState.detected_at.label("detected_at"),
            Asset.symbol.label("symbol"),
            Asset.is_active.label("is_active"),
        )
        .join(Asset, Asset.asset_id == HMMState.asset_id)
        .subquery()
    )

    latest_subquery = (
        select(
            ranked_subquery.c.asset_id,
            ranked_subquery.c.symbol,
            ranked_subquery.c.is_active,
            ranked_subquery.c.hmm_state_id,
            ranked_subquery.c.detected_at,
        )
        .distinct(ranked_subquery.c.asset_id)
        .order_by(
            ranked_subquery.c.asset_id,
            ranked_subquery.c.detected_at.desc(),
            ranked_subquery.c.hmm_state_id.desc(),
        )
        .subquery()
    )

    statement = (
        select(HMMState, latest_subquery.c.symbol)
        .join(latest_subquery, latest_subquery.c.hmm_state_id == HMMState.hmm_state_id)
        .order_by(desc(HMMState.detected_at), latest_subquery.c.symbol.asc())
    )
    if active_only:
        statement = statement.where(latest_subquery.c.is_active.is_(True))
    return statement


def list_latest_predictions(
    db: Session,
    *,
    active_only: bool = True,
    limit: int = 100,
) -> list[tuple[AIPrediction, str]]:
    safe_limit = max(1, min(limit, 100))
    return list(db.execute(_latest_predictions_query(active_only=active_only).limit(safe_limit)).all())


def get_latest_prediction_for_asset(db: Session, symbol: str) -> tuple[AIPrediction, str] | None:
    normalized_symbol = normalize_symbol(symbol)
    actual_priority = case(
        (AIPrediction.actual_price.is_not(None), 0),
        else_=1,
    )
    statement = (
        select(AIPrediction, Asset.symbol)
        .join(Asset, Asset.asset_id == AIPrediction.asset_id)
        .where(Asset.symbol == normalized_symbol)
        .order_by(actual_priority.asc(), AIPrediction.created_at.desc(), AIPrediction.prediction_id.desc())
        .limit(1)
    )
    return db.execute(statement).first()


def list_latest_signals(
    db: Session,
    *,
    active_only: bool = True,
    limit: int = 100,
) -> list[tuple[MarketSignal, str]]:
    safe_limit = max(1, min(limit, 100))
    return list(db.execute(_latest_signals_query(active_only=active_only).limit(safe_limit)).all())


def get_latest_signal_for_asset(db: Session, symbol: str) -> tuple[MarketSignal, str] | None:
    normalized_symbol = normalize_symbol(symbol)
    statement = (
        select(MarketSignal, Asset.symbol)
        .join(Asset, Asset.asset_id == MarketSignal.asset_id)
        .where(Asset.symbol == normalized_symbol)
        .order_by(MarketSignal.generated_at.desc(), MarketSignal.signal_id.desc())
        .limit(1)
    )
    return db.execute(statement).first()


def list_latest_regimes(
    db: Session,
    *,
    active_only: bool = True,
    limit: int = 100,
) -> list[tuple[HMMState, str]]:
    safe_limit = max(1, min(limit, 100))
    return list(db.execute(_latest_regimes_query(active_only=active_only).limit(safe_limit)).all())


def get_latest_regime_for_asset(db: Session, symbol: str) -> tuple[HMMState, str] | None:
    normalized_symbol = normalize_symbol(symbol)
    statement = (
        select(HMMState, Asset.symbol)
        .join(Asset, Asset.asset_id == HMMState.asset_id)
        .where(Asset.symbol == normalized_symbol)
        .order_by(HMMState.detected_at.desc(), HMMState.hmm_state_id.desc())
        .limit(1)
    )
    return db.execute(statement).first()

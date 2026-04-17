from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.price_prediction_model import load_recent_prices_for_asset
from app.db.models import AIPrediction, Asset, HMMState, MarketSignal, RiskIndicator
from app.etl.etl_utils import decimal_safe, normalize_symbol
from app.services.asset_service import get_asset_by_symbol


def _quantize_decimal(value: object, places: int) -> Decimal | None:
    decimal_value = decimal_safe(value)
    if decimal_value is None:
        return None
    return decimal_value.quantize(Decimal(f"1.{'0' * places}"), rounding=ROUND_HALF_UP)


def decide_signal(predicted_return: float, risk_label: str | None) -> str:
    if predicted_return < -0.02 or risk_label == "HIGH":
        return "SELL"
    if predicted_return > 0.02 and risk_label != "HIGH":
        return "BUY"
    return "HOLD"


def calculate_signal_strength(
    predicted_return: float,
    confidence: float | None,
    risk_label: str | None,
) -> float:
    magnitude_component = min(abs(predicted_return) * 12.0, 1.0)
    confidence_component = confidence if confidence is not None else 0.50
    score = (magnitude_component * 0.7) + (confidence_component * 0.3)
    if risk_label == "HIGH":
        score = max(score, 0.70)
    return float(max(0.05, min(1.0, score)))


def _latest_prediction_for_asset(db: Session, asset_id: object) -> AIPrediction | None:
    return db.scalar(
        select(AIPrediction)
        .where(AIPrediction.asset_id == asset_id)
        .order_by(AIPrediction.created_at.desc(), AIPrediction.prediction_id.desc())
        .limit(1)
    )


def _latest_risk_for_asset(db: Session, asset_id: object) -> RiskIndicator | None:
    return db.scalar(
        select(RiskIndicator)
        .where(RiskIndicator.asset_id == asset_id)
        .order_by(RiskIndicator.computed_at.desc(), RiskIndicator.risk_id.desc())
        .limit(1)
    )


def _latest_regime_for_asset(db: Session, asset_id: object) -> HMMState | None:
    return db.scalar(
        select(HMMState)
        .where(HMMState.asset_id == asset_id)
        .order_by(HMMState.detected_at.desc(), HMMState.hmm_state_id.desc())
        .limit(1)
    )


def generate_signal_for_asset(db: Session, symbol: str) -> MarketSignal:
    normalized_symbol = normalize_symbol(symbol)
    asset = get_asset_by_symbol(db, normalized_symbol)
    if asset is None:
        raise ValueError(f"Asset '{normalized_symbol}' does not exist.")

    prediction = _latest_prediction_for_asset(db, asset.asset_id)
    if prediction is None:
        raise ValueError(f"No ai_predictions row exists for '{normalized_symbol}'.")

    price_frame = load_recent_prices_for_asset(db, asset.asset_id, min_rows=1, limit=5)
    current_price = float(price_frame["close_price"].iloc[-1])
    if current_price <= 0:
        raise ValueError("Current price must be greater than zero to generate a signal.")

    risk_indicator = _latest_risk_for_asset(db, asset.asset_id)
    regime = _latest_regime_for_asset(db, asset.asset_id)

    predicted_return = (float(prediction.predicted_price) - current_price) / current_price
    confidence = float(prediction.confidence) if prediction.confidence is not None else None
    risk_label = risk_indicator.risk_label if risk_indicator is not None else None

    signal = MarketSignal(
        asset_id=asset.asset_id,
        signal_type=decide_signal(predicted_return, risk_label),
        model_source="RuleBasedSignal",
        strength=_quantize_decimal(
            calculate_signal_strength(predicted_return, confidence, risk_label),
            4,
        ),
        regime=regime.state_label if regime is not None else None,
    )
    db.add(signal)
    db.commit()
    db.refresh(signal)
    return signal


def generate_signals_for_all_active_assets(db: Session) -> list[dict[str, object]]:
    active_assets = list(
        db.scalars(
            select(Asset)
            .where(Asset.is_active.is_(True))
            .order_by(Asset.symbol.asc())
        ).all()
    )

    summary: list[dict[str, object]] = []
    for asset in active_assets:
        try:
            signal = generate_signal_for_asset(db, asset.symbol)
            summary.append(
                {
                    "symbol": asset.symbol,
                    "status": "SUCCESS",
                    "message": f"Signal {signal.signal_type} generated successfully.",
                    "created_at": signal.generated_at,
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

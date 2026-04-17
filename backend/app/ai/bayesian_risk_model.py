from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Asset, HMMState, RiskIndicator
from app.etl.etl_utils import decimal_safe, normalize_symbol
from app.services.asset_service import get_asset_by_symbol


def _quantize_decimal(value: object, places: int) -> Decimal | None:
    decimal_value = decimal_safe(value)
    if decimal_value is None:
        return None
    return decimal_value.quantize(Decimal(f"1.{'0' * places}"), rounding=ROUND_HALF_UP)


def clamp_risk_score(score: float) -> float:
    return float(max(0.0, min(1.0, score)))


def map_risk_label(score: float) -> str:
    if score >= 0.70:
        return "HIGH"
    if score >= 0.40:
        return "MEDIUM"
    return "LOW"


def _latest_hmm_state_for_asset(db: Session, asset_id: object) -> HMMState | None:
    return db.scalar(
        select(HMMState)
        .where(HMMState.asset_id == asset_id)
        .order_by(HMMState.detected_at.desc(), HMMState.hmm_state_id.desc())
        .limit(1)
    )


def _latest_risk_indicator_for_asset(db: Session, asset_id: object) -> RiskIndicator | None:
    return db.scalar(
        select(RiskIndicator)
        .where(RiskIndicator.asset_id == asset_id)
        .order_by(RiskIndicator.computed_at.desc(), RiskIndicator.risk_id.desc())
        .limit(1)
    )


def calculate_bayesian_style_risk_score(
    risk_indicator: RiskIndicator,
    regime_label: str | None,
) -> float:
    # Simplified probabilistic scoring for demo use, not a full Bayesian network.
    score = 0.30

    if risk_indicator.volatility_label == "HIGH":
        score += 0.25
    elif risk_indicator.volatility_label == "MEDIUM":
        score += 0.12

    if risk_indicator.momentum_label == "BEARISH":
        score += 0.15
    elif risk_indicator.momentum_label == "BULLISH":
        score -= 0.05

    if risk_indicator.volume_label == "SURGE":
        score += 0.10

    if regime_label == "BEAR":
        score += 0.10
    elif regime_label == "BULL":
        score -= 0.05

    if risk_indicator.beta is not None and float(risk_indicator.beta) > 1.2:
        score += 0.05

    if float(risk_indicator.price_vs_52w_high) > 0.20:
        score += 0.05

    return clamp_risk_score(score)


def compute_bayesian_risk_for_asset(db: Session, symbol: str) -> RiskIndicator:
    normalized_symbol = normalize_symbol(symbol)
    asset = get_asset_by_symbol(db, normalized_symbol)
    if asset is None:
        raise ValueError(f"Asset '{normalized_symbol}' does not exist.")

    risk_indicator = _latest_risk_indicator_for_asset(db, asset.asset_id)
    if risk_indicator is None:
        raise ValueError(
            f"No risk_indicators row exists for '{normalized_symbol}'. Run the risk indicator phase first."
        )

    hmm_state = _latest_hmm_state_for_asset(db, asset.asset_id)
    regime_label = hmm_state.state_label if hmm_state else None
    risk_score = calculate_bayesian_style_risk_score(risk_indicator, regime_label)

    risk_indicator.risk_score = _quantize_decimal(risk_score, 4)
    risk_indicator.risk_label = map_risk_label(risk_score)
    db.add(risk_indicator)
    db.commit()
    db.refresh(risk_indicator)
    return risk_indicator


def compute_bayesian_risk_for_all_active_assets(db: Session) -> list[dict[str, object]]:
    active_assets = list(
        db.scalars(
            select(Asset).where(Asset.is_active.is_(True)).order_by(Asset.symbol.asc())
        ).all()
    )

    summary: list[dict[str, object]] = []
    for asset in active_assets:
        try:
            updated_risk = compute_bayesian_risk_for_asset(db, asset.symbol)
            summary.append(
                {
                    "symbol": asset.symbol,
                    "status": "SUCCESS",
                    "message": f"Risk score updated to {updated_risk.risk_label}.",
                    "created_at": updated_risk.computed_at,
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

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.price_prediction_model import load_recent_prices_for_asset
from app.db.models import Asset, HMMState
from app.etl.etl_utils import decimal_safe, normalize_symbol, utc_now
from app.services.asset_service import get_asset_by_symbol


REGIME_TO_INDEX = {
    "BULL": 0,
    "BEAR": 1,
    "SIDEWAYS": 2,
}


def _quantize_decimal(value: object, places: int) -> Decimal | None:
    decimal_value = decimal_safe(value)
    if decimal_value is None:
        return None
    return decimal_value.quantize(Decimal(f"1.{'0' * places}"), rounding=ROUND_HALF_UP)


def detect_regime_from_prices(price_rows: pd.DataFrame | pd.Series) -> dict[str, object]:
    if isinstance(price_rows, pd.DataFrame):
        if "close_price" in price_rows.columns:
            close_series = price_rows["close_price"]
        elif "Close" in price_rows.columns:
            close_series = price_rows["Close"]
        else:
            raise ValueError("Price data must include close_price or Close.")
    else:
        close_series = price_rows

    closes = pd.to_numeric(close_series, errors="coerce").dropna()
    returns = closes.pct_change().dropna()
    if len(returns) < 10:
        raise ValueError("At least 10 return observations are required for regime detection.")

    recent_returns = returns.tail(min(30, len(returns)))
    average_return = float(recent_returns.mean())
    volatility = float(recent_returns.std()) if len(recent_returns) > 1 else 0.0
    noise_band = max(volatility * 0.25, 0.001)

    if average_return > noise_band:
        state_label = "BULL"
    elif average_return < -noise_band:
        state_label = "BEAR"
    else:
        state_label = "SIDEWAYS"

    signal_ratio = abs(average_return) / (volatility + 1e-6)
    if state_label == "SIDEWAYS":
        probability = max(0.50, min(0.95, 1.0 - min(signal_ratio, 0.45)))
    else:
        probability = max(0.51, min(0.95, signal_ratio))

    return {
        "state_label": state_label,
        "state_index": REGIME_TO_INDEX[state_label],
        "probability": probability,
    }


def run_regime_detection_for_asset(db: Session, symbol: str) -> HMMState:
    normalized_symbol = normalize_symbol(symbol)
    asset = get_asset_by_symbol(db, normalized_symbol)
    if asset is None:
        raise ValueError(f"Asset '{normalized_symbol}' does not exist.")

    price_frame = load_recent_prices_for_asset(db, asset.asset_id, min_rows=20, limit=180)
    regime = detect_regime_from_prices(price_frame)

    hmm_state = HMMState(
        asset_id=asset.asset_id,
        state_label=regime["state_label"],
        state_index=regime["state_index"],
        probability=_quantize_decimal(regime["probability"], 5),
        detected_at=utc_now(),
    )
    db.add(hmm_state)
    db.commit()
    db.refresh(hmm_state)
    return hmm_state


def run_regime_detection_for_all_active_assets(db: Session) -> list[dict[str, object]]:
    active_assets = list(
        db.scalars(
            select(Asset).where(Asset.is_active.is_(True)).order_by(Asset.symbol.asc())
        ).all()
    )

    summary: list[dict[str, object]] = []
    for asset in active_assets:
        try:
            state = run_regime_detection_for_asset(db, asset.symbol)
            summary.append(
                {
                    "symbol": asset.symbol,
                    "status": "SUCCESS",
                    "message": "Regime detected successfully.",
                    "created_at": state.detected_at,
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

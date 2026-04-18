from __future__ import annotations

from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AIPrediction, Asset, PriceHistory
from app.etl.etl_utils import decimal_safe, normalize_symbol
from app.services.asset_service import get_asset_by_symbol


PREFERRED_INTERVALS = ("1d", "1h", "5min")


def _next_prediction_timestamp(price_frame: pd.DataFrame) -> object:
    latest_row = price_frame.iloc[-1]
    latest_recorded_at = latest_row["recorded_at"]
    interval = latest_row.get("interval")

    if interval == "5min":
        return latest_recorded_at + timedelta(minutes=5)
    if interval == "1h":
        return latest_recorded_at + timedelta(hours=1)
    return latest_recorded_at + timedelta(days=1)


def _quantize_decimal(value: object, places: int) -> Decimal | None:
    decimal_value = decimal_safe(value)
    if decimal_value is None:
        return None
    return decimal_value.quantize(Decimal(f"1.{'0' * places}"), rounding=ROUND_HALF_UP)


def load_recent_prices_for_asset(
    db: Session,
    asset_id: object,
    *,
    min_rows: int = 2,
    limit: int = 180,
) -> pd.DataFrame:
    for interval in PREFERRED_INTERVALS:
        rows = list(
            db.scalars(
                select(PriceHistory)
                .where(
                    PriceHistory.asset_id == asset_id,
                    PriceHistory.interval == interval,
                )
                .order_by(PriceHistory.recorded_at.desc())
                .limit(limit)
            ).all()
        )
        if len(rows) >= min_rows:
            rows.reverse()
            return pd.DataFrame(
                [
                    {
                        "recorded_at": row.recorded_at,
                        "close_price": float(row.close_price),
                        "interval": row.interval,
                    }
                    for row in rows
                ]
            )

    rows = list(
        db.scalars(
            select(PriceHistory)
            .where(PriceHistory.asset_id == asset_id)
            .order_by(PriceHistory.recorded_at.desc())
            .limit(limit)
        ).all()
    )
    if len(rows) < min_rows:
        raise ValueError("Not enough stored price_history rows exist for this asset.")

    rows.reverse()
    return pd.DataFrame(
        [
            {
                "recorded_at": row.recorded_at,
                "close_price": float(row.close_price),
                "interval": row.interval,
            }
            for row in rows
        ]
    )


def _calculate_prediction_confidence(close_series: pd.Series, r2_score: float) -> float:
    returns = close_series.pct_change().dropna()
    volatility = float(returns.tail(30).std()) if not returns.empty else 0.0
    fit_component = max(0.0, min(1.0, r2_score if np.isfinite(r2_score) else 0.0))
    stability_component = max(0.0, 1.0 - min(volatility * 10.0, 1.0))
    confidence = (fit_component * 0.7) + (stability_component * 0.3)
    return float(max(0.1, min(0.95, confidence)))


def predict_price_for_asset(db: Session, symbol: str) -> AIPrediction:
    normalized_symbol = normalize_symbol(symbol)
    asset = get_asset_by_symbol(db, normalized_symbol)
    if asset is None:
        raise ValueError(f"Asset '{normalized_symbol}' does not exist.")

    price_frame = load_recent_prices_for_asset(db, asset.asset_id, min_rows=10, limit=180)
    close_series = pd.to_numeric(price_frame["close_price"], errors="coerce").dropna()
    if len(close_series) < 10:
        raise ValueError("At least 10 close-price rows are required for prediction.")

    x_values = np.arange(len(close_series), dtype=float).reshape(-1, 1)
    y_values = close_series.to_numpy(dtype=float)

    model = LinearRegression()
    model.fit(x_values, y_values)

    predicted_price_raw = float(model.predict([[len(close_series)]])[0])
    predicted_price = max(predicted_price_raw, 0.0)
    model_score = float(model.score(x_values, y_values))
    confidence = _calculate_prediction_confidence(close_series, model_score)

    prediction = AIPrediction(
        asset_id=asset.asset_id,
        model_type="LinearRegression",
        predicted_price=_quantize_decimal(predicted_price, 6),
        confidence=_quantize_decimal(confidence, 4),
        predicted_for=_next_prediction_timestamp(price_frame),
        actual_price=None,
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction


def predict_prices_for_all_active_assets(db: Session) -> list[dict[str, object]]:
    active_assets = list(
        db.scalars(
            select(Asset).where(Asset.is_active.is_(True)).order_by(Asset.symbol.asc())
        ).all()
    )

    summary: list[dict[str, object]] = []
    for asset in active_assets:
        try:
            prediction = predict_price_for_asset(db, asset.symbol)
            summary.append(
                {
                    "symbol": asset.symbol,
                    "status": "SUCCESS",
                    "message": "Prediction created successfully.",
                    "created_at": prediction.created_at,
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

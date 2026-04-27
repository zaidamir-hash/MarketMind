from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.db.models import AIPrediction, Asset, PriceHistory
from app.etl.etl_utils import normalize_symbol, utc_now


PRICE_LOOKAHEAD_WINDOW = timedelta(days=7)


@dataclass(slots=True)
class PredictionActualMatch:
    recorded_at: object
    close_price: Decimal
    interval: str


def find_best_actual_price_for_prediction(
    db: Session,
    prediction: AIPrediction,
) -> PredictionActualMatch | None:
    price_row = db.execute(
        select(
            PriceHistory.recorded_at,
            PriceHistory.close_price,
            PriceHistory.interval,
        )
        .where(
            PriceHistory.asset_id == prediction.asset_id,
            PriceHistory.recorded_at >= prediction.predicted_for,
            PriceHistory.recorded_at <= prediction.predicted_for + PRICE_LOOKAHEAD_WINDOW,
        )
        .order_by(PriceHistory.recorded_at.asc(), PriceHistory.interval.asc())
        .limit(1)
    ).first()

    if price_row is None:
        return None

    recorded_at, close_price, interval = price_row
    return PredictionActualMatch(
        recorded_at=recorded_at,
        close_price=close_price,
        interval=interval,
    )


def _matured_predictions_query(symbol: str | None = None) -> Select[tuple[AIPrediction, str]]:
    statement = (
        select(AIPrediction, Asset.symbol)
        .join(Asset, Asset.asset_id == AIPrediction.asset_id)
        .where(
            AIPrediction.actual_price.is_(None),
            AIPrediction.predicted_for <= utc_now(),
        )
        .order_by(AIPrediction.predicted_for.asc(), AIPrediction.created_at.asc())
    )

    if symbol:
        normalized_symbol = normalize_symbol(symbol)
        statement = statement.where(Asset.symbol == normalized_symbol)

    return statement


def reconcile_prediction_actuals(
    db: Session,
    symbol: str | None = None,
) -> dict[str, object]:
    predictions = list(db.execute(_matured_predictions_query(symbol=symbol)).all())

    updated = 0
    scanned = len(predictions)

    for prediction, _asset_symbol in predictions:
        match = find_best_actual_price_for_prediction(db, prediction)
        if match is None:
            continue

        prediction.actual_price = match.close_price
        updated += 1

    if updated > 0:
        db.commit()

    remaining_statement = (
        select(func.count())
        .select_from(AIPrediction)
        .join(Asset, Asset.asset_id == AIPrediction.asset_id)
        .where(
            AIPrediction.actual_price.is_(None),
            AIPrediction.predicted_for <= utc_now(),
        )
    )
    if symbol:
        remaining_statement = remaining_statement.where(Asset.symbol == normalize_symbol(symbol))

    remaining = db.scalar(remaining_statement)

    return {
        "status": "SUCCESS",
        "message": "Prediction actual-price reconciliation completed.",
        "symbol": normalize_symbol(symbol) if symbol else None,
        "scanned": scanned,
        "updated": updated,
        "remaining": remaining or 0,
    }


def reconcile_matured_predictions_for_all_assets(db: Session) -> dict[str, object]:
    return reconcile_prediction_actuals(db)

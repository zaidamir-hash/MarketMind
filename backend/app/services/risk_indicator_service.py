from __future__ import annotations

from decimal import Decimal
from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.models import Asset, RiskIndicator
from app.etl.etl_utils import decimal_safe, normalize_symbol
from app.etl.risk_feature_builder import build_risk_features_from_history
from app.etl.yfinance_client import fetch_asset_metadata, fetch_price_history
from app.services.asset_service import get_asset_by_symbol
from app.services.scraper_log_service import (
    create_scraper_log_start,
    finish_scraper_log_fail,
    finish_scraper_log_success,
)


def _round_decimal(value: object, places: int) -> Decimal | None:
    decimal_value = decimal_safe(value)
    if decimal_value is None:
        return None
    return decimal_value.quantize(Decimal(f"1.{'0' * places}"))


def _market_cap_category_from_metadata(metadata: dict[str, Any]) -> str | None:
    # Thresholds are not documented in the repo, so this phase keeps the category NULL.
    del metadata
    return None


def _latest_risk_query(active_only: bool = True):
    ranked_subquery = (
        select(
            RiskIndicator.risk_id.label("risk_id"),
            RiskIndicator.asset_id.label("asset_id"),
            RiskIndicator.computed_at.label("computed_at"),
            Asset.symbol.label("symbol"),
            Asset.is_active.label("is_active"),
        )
        .join(Asset, Asset.asset_id == RiskIndicator.asset_id)
        .subquery()
    )

    latest_computed_subquery = (
        select(
            ranked_subquery.c.asset_id,
            ranked_subquery.c.symbol,
            ranked_subquery.c.is_active,
            ranked_subquery.c.risk_id,
            ranked_subquery.c.computed_at,
        )
        .distinct(ranked_subquery.c.asset_id)
        .order_by(ranked_subquery.c.asset_id, ranked_subquery.c.computed_at.desc(), ranked_subquery.c.risk_id.desc())
        .subquery()
    )

    statement = (
        select(RiskIndicator, latest_computed_subquery.c.symbol)
        .join(latest_computed_subquery, latest_computed_subquery.c.risk_id == RiskIndicator.risk_id)
        .order_by(desc(RiskIndicator.computed_at), latest_computed_subquery.c.symbol.asc())
    )
    if active_only:
        statement = statement.where(latest_computed_subquery.c.is_active.is_(True))
    return statement


def compute_risk_indicators_for_asset(db: Session, symbol: str) -> RiskIndicator:
    normalized_symbol = normalize_symbol(symbol)
    log = create_scraper_log_start(db, f"risk_indicators_{normalized_symbol}")

    try:
        asset = get_asset_by_symbol(db, normalized_symbol)
        if asset is None:
            raise ValueError(f"Asset '{normalized_symbol}' does not exist. Onboard it first.")

        metadata = fetch_asset_metadata(normalized_symbol)
        history = fetch_price_history(normalized_symbol, period="1y", interval="1d")
        feature_set = build_risk_features_from_history(history, metadata=metadata)

        risk_indicator = RiskIndicator(
            asset_id=asset.asset_id,
            beta=_round_decimal(metadata.get("raw_info", {}).get("beta"), 4),
            volatility_30d=_round_decimal(feature_set["volatility_30d"], 6),
            rsi_14=_round_decimal(feature_set["rsi_14"], 2),
            volume_ratio=_round_decimal(feature_set["volume_ratio"], 4),
            price_vs_52w_high=_round_decimal(feature_set["price_vs_52w_high"], 4),
            price_vs_sma50=_round_decimal(feature_set["price_vs_sma50"], 4),
            market_cap_cat=_market_cap_category_from_metadata(metadata),
            volatility_label=feature_set["volatility_label"],
            momentum_label=feature_set["momentum_label"],
            volume_label=feature_set["volume_label"],
            risk_score=None,
            risk_label=None,
        )

        db.add(risk_indicator)
        db.commit()
        db.refresh(risk_indicator)
        finish_scraper_log_success(db, log, rows_inserted=1)
        return risk_indicator
    except Exception as exc:
        db.rollback()
        finish_scraper_log_fail(db, log, str(exc))
        raise


def compute_risk_indicators_for_all_active_assets(db: Session) -> list[dict[str, object]]:
    active_assets = list(
        db.scalars(
            select(Asset).where(Asset.is_active.is_(True)).order_by(Asset.symbol.asc())
        ).all()
    )

    summary: list[dict[str, object]] = []
    for asset in active_assets:
        try:
            indicator = compute_risk_indicators_for_asset(db, asset.symbol)
            summary.append(
                {
                    "symbol": asset.symbol,
                    "status": "SUCCESS",
                    "message": "Risk indicators computed successfully.",
                    "computed_at": indicator.computed_at,
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


def get_latest_risk_indicator_for_asset(db: Session, symbol: str) -> tuple[RiskIndicator, str] | None:
    normalized_symbol = normalize_symbol(symbol)
    statement = (
        select(RiskIndicator, Asset.symbol)
        .join(Asset, Asset.asset_id == RiskIndicator.asset_id)
        .where(Asset.symbol == normalized_symbol)
        .order_by(RiskIndicator.computed_at.desc(), RiskIndicator.risk_id.desc())
        .limit(1)
    )
    return db.execute(statement).first()


def list_latest_risk_indicators(
    db: Session,
    active_only: bool = True,
    limit: int = 100,
) -> list[tuple[RiskIndicator, str]]:
    safe_limit = max(1, min(limit, 100))
    statement = _latest_risk_query(active_only=active_only).limit(safe_limit)
    return list(db.execute(statement).all())

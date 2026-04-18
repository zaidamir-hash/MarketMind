from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.db.models import Asset, PriceHistory, ScraperLog
from app.etl.etl_utils import (
    decimal_safe,
    interval_to_yfinance,
    int_safe,
    normalize_interval,
    normalize_symbol,
    utc_datetime_safe,
)
from app.etl.yfinance_client import fetch_asset_metadata, fetch_price_history
from app.services.asset_service import get_asset_by_symbol
from app.services.scraper_log_service import (
    create_scraper_log_start,
    finish_scraper_log_fail,
    finish_scraper_log_success,
)


def onboard_asset_from_yfinance(db: Session, symbol: str) -> Asset:
    normalized_symbol = normalize_symbol(symbol)
    log = create_scraper_log_start(db, f"yfinance_onboard_{normalized_symbol}")

    try:
        metadata = fetch_asset_metadata(normalized_symbol)
        asset = get_asset_by_symbol(db, normalized_symbol)

        if asset is None:
            asset = Asset(
                symbol=metadata["symbol"],
                name=metadata["name"],
                asset_type=metadata["asset_type"],
                exchange=metadata["exchange"],
                currency=metadata["currency"],
                is_active=True,
            )
            db.add(asset)
        else:
            asset.name = metadata["name"] or asset.name
            asset.asset_type = metadata["asset_type"] or asset.asset_type
            asset.exchange = metadata["exchange"] or asset.exchange
            asset.currency = metadata["currency"] or asset.currency
            asset.is_active = True

        db.commit()
        db.refresh(asset)
        finish_scraper_log_success(db, log, rows_inserted=1)
        return asset
    except Exception as exc:
        db.rollback()
        finish_scraper_log_fail(db, log, str(exc))
        raise


def fetch_prices_for_asset(
    db: Session,
    symbol: str,
    period: str = "5d",
    interval: str = "5m",
) -> int:
    normalized_symbol = normalize_symbol(symbol)
    normalized_interval = normalize_interval(interval)
    yfinance_interval = interval_to_yfinance(interval)
    log = create_scraper_log_start(db, f"yfinance_prices_{normalized_symbol}_{normalized_interval}")

    try:
        asset = get_asset_by_symbol(db, normalized_symbol)
        if asset is None:
            raise ValueError(
                f"Asset '{normalized_symbol}' does not exist. Onboard it first."
            )

        history = fetch_price_history(normalized_symbol, period=period, interval=yfinance_interval)
        if history.empty:
            finish_scraper_log_success(db, log, rows_inserted=0)
            return 0

        rows_to_insert: list[dict[str, object]] = []
        for recorded_at, row in history.iterrows():
            open_price = decimal_safe(row.get("Open"))
            high_price = decimal_safe(row.get("High"))
            low_price = decimal_safe(row.get("Low"))
            close_price = decimal_safe(row.get("Close"))
            volume = int_safe(row.get("Volume"))
            timestamp = utc_datetime_safe(recorded_at)

            if None in (open_price, high_price, low_price, close_price, timestamp):
                continue

            if volume is None:
                volume = 0

            rows_to_insert.append(
                {
                    "asset_id": asset.asset_id,
                    "open_price": open_price,
                    "close_price": close_price,
                    "high_price": high_price,
                    "low_price": low_price,
                    "volume": volume,
                    "interval": normalized_interval,
                    "recorded_at": timestamp,
                }
            )

        if not rows_to_insert:
            finish_scraper_log_success(db, log, rows_inserted=0)
            return 0

        insert_stmt = insert(PriceHistory).values(rows_to_insert)
        insert_stmt = insert_stmt.on_conflict_do_nothing(
            constraint="uq_price_asset_time_interval"
        )
        result = db.execute(insert_stmt)
        db.commit()

        inserted_count = result.rowcount if result.rowcount is not None and result.rowcount > 0 else 0
        finish_scraper_log_success(db, log, rows_inserted=inserted_count)
        return inserted_count
    except Exception as exc:
        db.rollback()
        finish_scraper_log_fail(db, log, str(exc))
        raise


def fetch_prices_for_all_active_assets(
    db: Session,
    period: str = "5d",
    interval: str = "5m",
) -> list[dict[str, object]]:
    active_assets = list(
        db.scalars(
            select(Asset).where(Asset.is_active.is_(True)).order_by(Asset.symbol.asc())
        ).all()
    )

    summary: list[dict[str, object]] = []
    for asset in active_assets:
        try:
            rows_inserted = fetch_prices_for_asset(
                db,
                asset.symbol,
                period=period,
                interval=interval,
            )
            summary.append(
                {
                    "symbol": asset.symbol,
                    "status": "SUCCESS",
                    "rows_inserted": rows_inserted,
                }
            )
        except Exception as exc:
            summary.append(
                {
                    "symbol": asset.symbol,
                    "status": "FAIL",
                    "rows_inserted": 0,
                    "message": str(exc),
                }
            )
    return summary


def list_recent_scraper_logs(db: Session, limit: int = 20) -> list[ScraperLog]:
    safe_limit = max(1, min(limit, 100))
    return list(
        db.scalars(
            select(ScraperLog)
            .order_by(ScraperLog.started_at.desc())
            .limit(safe_limit)
        ).all()
    )

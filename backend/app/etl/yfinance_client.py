from __future__ import annotations

from typing import Any

import pandas as pd
import yfinance as yf

from app.etl.etl_utils import classify_asset_type, normalize_symbol


def get_ticker(symbol: str) -> yf.Ticker:
    return yf.Ticker(normalize_symbol(symbol))


def fetch_asset_metadata(symbol: str) -> dict[str, Any]:
    normalized_symbol = normalize_symbol(symbol)
    ticker = get_ticker(normalized_symbol)

    info: dict[str, Any] = {}
    try:
        info = ticker.info or {}
    except Exception:
        info = {}

    fast_info: dict[str, Any] = {}
    try:
        fast_info = dict(getattr(ticker, "fast_info", {}) or {})
    except Exception:
        fast_info = {}

    name = (
        info.get("longName")
        or info.get("shortName")
        or info.get("displayName")
        or normalized_symbol
    )
    exchange = info.get("exchange") or fast_info.get("exchange")
    currency = (
        info.get("currency")
        or fast_info.get("currency")
        or "USD"
    )

    metadata: dict[str, Any] = {
        "symbol": normalized_symbol,
        "name": str(name),
        "asset_type": classify_asset_type(normalized_symbol, info | fast_info),
        "exchange": str(exchange) if exchange else None,
        "currency": str(currency).upper(),
        "is_active": True,
        "raw_info": info,
    }
    return metadata


def fetch_price_history(symbol: str, period: str = "5d", interval: str = "5m") -> pd.DataFrame:
    ticker = get_ticker(symbol)
    history = ticker.history(period=period, interval=interval, auto_adjust=False)
    if history is None or history.empty:
        return pd.DataFrame()
    return history

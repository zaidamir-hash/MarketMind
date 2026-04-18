from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

import pandas as pd


def normalize_symbol(symbol: str) -> str:
    return symbol.strip().upper()


def normalize_interval(interval: str) -> str:
    normalized = interval.strip().lower()
    mapping = {
        "5m": "5min",
        "5min": "5min",
        "1h": "1h",
        "60m": "1h",
        "1d": "1d",
        "1day": "1d",
    }
    if normalized not in mapping:
        raise ValueError("Unsupported interval. Use 5m, 1h, or 1d.")
    return mapping[normalized]


def interval_to_yfinance(interval: str) -> str:
    canonical_interval = normalize_interval(interval)
    mapping = {
        "5min": "5m",
        "1h": "1h",
        "1d": "1d",
    }
    return mapping[canonical_interval]


def decimal_safe(value: object) -> Decimal | None:
    if value is None or pd.isna(value):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def int_safe(value: object) -> int | None:
    if value is None or pd.isna(value):
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def utc_datetime_safe(value: object) -> datetime | None:
    if value is None or pd.isna(value):
        return None
    timestamp = pd.Timestamp(value)
    if timestamp.tzinfo is None:
        timestamp = timestamp.tz_localize("UTC")
    else:
        timestamp = timestamp.tz_convert("UTC")
    return timestamp.to_pydatetime()


def classify_asset_type(symbol: str, metadata: dict[str, object]) -> str:
    normalized_symbol = normalize_symbol(symbol)
    quote_type = str(metadata.get("quoteType") or "").upper()
    instrument_type = str(metadata.get("instrumentType") or "").upper()
    if normalized_symbol.endswith("-USD") or quote_type == "CRYPTOCURRENCY" or instrument_type == "CRYPTOCURRENCY":
        return "CRYPTO"
    return "STOCK"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)

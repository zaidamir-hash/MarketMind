from __future__ import annotations

from typing import Any

import pandas as pd


def _require_non_empty_series(series: pd.Series, label: str) -> pd.Series:
    cleaned = pd.to_numeric(series, errors="coerce").dropna()
    if cleaned.empty:
        raise ValueError(f"{label} data is empty.")
    return cleaned


def compute_returns(close_series: pd.Series) -> pd.Series:
    closes = _require_non_empty_series(close_series, "Close price")
    returns = closes.pct_change().dropna()
    if returns.empty:
        raise ValueError("Not enough close-price history to compute returns.")
    return returns


def compute_volatility_30d(close_series: pd.Series) -> float:
    returns = compute_returns(close_series)
    latest_returns = returns.tail(30)
    if len(latest_returns) < 30:
        raise ValueError("At least 31 valid close prices are required to compute volatility_30d.")
    return float(latest_returns.std())


def compute_rsi_14(close_series: pd.Series) -> float:
    closes = _require_non_empty_series(close_series, "Close price")
    if len(closes) < 15:
        raise ValueError("At least 15 valid close prices are required to compute rsi_14.")

    deltas = closes.diff().dropna()
    if len(deltas) < 14:
        raise ValueError("Insufficient close-price history to compute rsi_14.")

    gains = deltas.clip(lower=0)
    losses = -deltas.clip(upper=0)

    avg_gain = gains.rolling(window=14, min_periods=14).mean()
    avg_loss = losses.rolling(window=14, min_periods=14).mean()

    if avg_gain.dropna().empty or avg_loss.dropna().empty:
        raise ValueError("Insufficient data to compute rsi_14 rolling averages.")

    latest_gain = float(avg_gain.dropna().iloc[-1])
    latest_loss = float(avg_loss.dropna().iloc[-1])

    if latest_loss == 0:
        rsi = 100.0
    else:
        relative_strength = latest_gain / latest_loss
        rsi = 100.0 - (100.0 / (1.0 + relative_strength))

    return float(max(0.0, min(100.0, rsi)))


def compute_volume_ratio(volume_series: pd.Series) -> float:
    volumes = _require_non_empty_series(volume_series, "Volume")
    latest_volumes = volumes.tail(30)
    if len(latest_volumes) < 30:
        raise ValueError("At least 30 valid volume rows are required to compute volume_ratio.")

    average_volume = float(latest_volumes.mean())
    if average_volume <= 0:
        raise ValueError("Average volume must be greater than zero to compute volume_ratio.")

    latest_volume = float(latest_volumes.iloc[-1])
    return latest_volume / average_volume


def compute_price_vs_52w_high(history_df: pd.DataFrame) -> float:
    if history_df.empty:
        raise ValueError("History data is empty.")

    high_series = pd.to_numeric(history_df.get("High"), errors="coerce").dropna()
    close_series = _require_non_empty_series(history_df.get("Close"), "Close price")

    current_close = float(close_series.iloc[-1])
    high_52w = float(high_series.max()) if not high_series.empty else float(close_series.max())

    if high_52w <= 0:
        raise ValueError("52-week high must be greater than zero.")

    return (high_52w - current_close) / high_52w


def compute_price_vs_sma50(close_series: pd.Series) -> float:
    closes = _require_non_empty_series(close_series, "Close price")
    latest_closes = closes.tail(50)
    if len(latest_closes) < 50:
        raise ValueError("At least 50 valid close prices are required to compute price_vs_sma50.")

    sma50 = float(latest_closes.mean())
    if sma50 <= 0:
        raise ValueError("SMA50 must be greater than zero.")

    current_close = float(latest_closes.iloc[-1])
    return (current_close - sma50) / sma50


def label_volatility(volatility_30d: float) -> str:
    if volatility_30d > 0.03:
        return "HIGH"
    if volatility_30d > 0.015:
        return "MEDIUM"
    return "LOW"


def label_momentum(rsi_14: float) -> str:
    if rsi_14 > 60:
        return "BULLISH"
    if rsi_14 < 40:
        return "BEARISH"
    return "NEUTRAL"


def label_volume(volume_ratio: float) -> str:
    if volume_ratio > 1.5:
        return "SURGE"
    if volume_ratio < 0.7:
        return "LOW"
    return "NORMAL"


def build_risk_features_from_history(
    history_df: pd.DataFrame,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    del metadata

    if history_df is None or history_df.empty:
        raise ValueError("No daily history returned for risk indicator computation.")

    closes = history_df.get("Close")
    volumes = history_df.get("Volume")
    if closes is None or volumes is None:
        raise ValueError("History data must include Close and Volume columns.")

    volatility_30d = compute_volatility_30d(closes)
    rsi_14 = compute_rsi_14(closes)
    volume_ratio = compute_volume_ratio(volumes)
    price_vs_52w_high = compute_price_vs_52w_high(history_df)
    price_vs_sma50 = compute_price_vs_sma50(closes)

    return {
        "volatility_30d": volatility_30d,
        "rsi_14": rsi_14,
        "volume_ratio": volume_ratio,
        "price_vs_52w_high": price_vs_52w_high,
        "price_vs_sma50": price_vs_sma50,
        "volatility_label": label_volatility(volatility_30d),
        "momentum_label": label_momentum(rsi_14),
        "volume_label": label_volume(volume_ratio),
    }

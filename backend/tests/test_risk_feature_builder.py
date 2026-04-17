from __future__ import annotations

import pandas as pd

from app.etl.risk_feature_builder import (
    compute_rsi_14,
    label_momentum,
    label_volatility,
    label_volume,
)


def test_label_volatility_thresholds() -> None:
    assert label_volatility(0.031) == "HIGH"
    assert label_volatility(0.02) == "MEDIUM"
    assert label_volatility(0.01) == "LOW"


def test_label_momentum_thresholds() -> None:
    assert label_momentum(61) == "BULLISH"
    assert label_momentum(39) == "BEARISH"
    assert label_momentum(50) == "NEUTRAL"


def test_label_volume_thresholds() -> None:
    assert label_volume(1.6) == "SURGE"
    assert label_volume(0.6) == "LOW"
    assert label_volume(1.0) == "NORMAL"


def test_compute_rsi_14_stays_in_bounds() -> None:
    close_series = pd.Series(
        [100, 101, 102, 103, 102, 104, 105, 104, 106, 107, 106, 108, 109, 110, 111, 112]
    )
    rsi = compute_rsi_14(close_series)
    assert 0 <= rsi <= 100

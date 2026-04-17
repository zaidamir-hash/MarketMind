from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

import numpy as np
import pandas as pd

from app.etl.etl_utils import decimal_safe


def _quantize_decimal(value: object, places: int) -> Decimal | None:
    decimal_value = decimal_safe(value)
    if decimal_value is None:
        return None
    return decimal_value.quantize(Decimal(f"1.{'0' * places}"), rounding=ROUND_HALF_UP)


def build_returns_matrix(price_series_by_symbol: dict[str, pd.Series]) -> pd.DataFrame:
    frame = pd.DataFrame(price_series_by_symbol).sort_index()
    frame = frame.dropna(how="all")
    if frame.empty:
        raise ValueError("No overlapping price history exists for optimization.")

    returns_matrix = frame.pct_change().dropna(how="any")
    if returns_matrix.empty or len(returns_matrix.columns) < 2:
        raise ValueError("At least two assets with overlapping return history are required.")
    if len(returns_matrix) < 20:
        raise ValueError("Optimization requires at least 20 overlapping return rows.")
    return returns_matrix


def calculate_portfolio_metrics(weights: np.ndarray, returns_matrix: pd.DataFrame) -> dict[str, float]:
    mean_returns = returns_matrix.mean().to_numpy(dtype=float)
    covariance = returns_matrix.cov().to_numpy(dtype=float)
    annual_factor = 252.0

    expected_return = float(np.dot(weights, mean_returns) * annual_factor)
    expected_risk = float(np.sqrt(np.dot(weights.T, np.dot(covariance * annual_factor, weights))))
    sharpe_ratio = 0.0 if expected_risk <= 0 else expected_return / expected_risk

    return {
        "expected_return": expected_return,
        "expected_risk": expected_risk,
        "sharpe_ratio": sharpe_ratio,
    }


def random_weight_search(
    returns_matrix: pd.DataFrame,
    *,
    iterations: int = 250,
    seed: int = 42,
) -> dict[str, object]:
    asset_count = len(returns_matrix.columns)
    if asset_count < 2:
        raise ValueError("Portfolio optimization requires at least two assets.")

    rng = np.random.default_rng(seed)
    best_result: dict[str, object] | None = None

    for _ in range(iterations):
        weights = rng.random(asset_count)
        weights = weights / weights.sum()
        metrics = calculate_portfolio_metrics(weights, returns_matrix)

        if best_result is None or metrics["sharpe_ratio"] > best_result["sharpe_ratio"]:
            best_result = {
                "weights": weights,
                **metrics,
            }

    if best_result is None:
        raise ValueError("Portfolio optimization could not find a valid weight set.")
    return best_result


def optimize_portfolio_weights(
    returns_matrix: pd.DataFrame,
    *,
    iterations: int = 250,
) -> dict[str, object]:
    result = random_weight_search(returns_matrix, iterations=iterations)
    weights = result["weights"]
    symbols = list(returns_matrix.columns)
    return {
        "weights": {
            symbol: round(float(weight), 6)
            for symbol, weight in zip(symbols, weights, strict=True)
        },
        "expected_return": _quantize_decimal(result["expected_return"], 4),
        "expected_risk": _quantize_decimal(result["expected_risk"], 4),
        "sharpe_ratio": _quantize_decimal(result["sharpe_ratio"], 4),
        "generations_run": iterations,
    }

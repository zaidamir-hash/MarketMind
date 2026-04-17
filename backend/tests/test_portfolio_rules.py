from __future__ import annotations

import numpy as np
import pandas as pd

from app.ai.portfolio_optimizer import calculate_portfolio_metrics, optimize_portfolio_weights


def test_optimize_portfolio_weights_normalizes_weights() -> None:
    returns_matrix = pd.DataFrame(
        {
            "AAPL": [
                0.01, 0.02, -0.01, 0.03, 0.01, 0.02, -0.01, 0.02, 0.01, 0.00,
                0.01, 0.02, -0.01, 0.03, 0.01, 0.02, -0.01, 0.02, 0.01, 0.00,
            ],
            "MSFT": [
                0.00, 0.01, 0.02, 0.01, -0.01, 0.02, 0.01, 0.00, 0.02, 0.01,
                0.00, 0.01, 0.02, 0.01, -0.01, 0.02, 0.01, 0.00, 0.02, 0.01,
            ],
        }
    )
    result = optimize_portfolio_weights(returns_matrix, iterations=100)
    assert abs(sum(result["weights"].values()) - 1.0) < 1e-6


def test_calculate_portfolio_metrics_returns_non_negative_risk() -> None:
    returns_matrix = pd.DataFrame(
        {
            "AAPL": [0.01, 0.02, -0.01, 0.03],
            "MSFT": [0.00, 0.01, 0.02, 0.01],
        }
    )
    metrics = calculate_portfolio_metrics(np.array([0.5, 0.5]), returns_matrix)
    assert metrics["expected_risk"] >= 0

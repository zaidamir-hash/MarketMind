from __future__ import annotations

from app.ai.bayesian_risk_model import clamp_risk_score, map_risk_label
from app.ai.signal_generator import decide_signal


def test_clamp_risk_score_bounds() -> None:
    assert clamp_risk_score(-0.5) == 0.0
    assert clamp_risk_score(1.5) == 1.0
    assert clamp_risk_score(0.42) == 0.42


def test_map_risk_label_thresholds() -> None:
    assert map_risk_label(0.70) == "HIGH"
    assert map_risk_label(0.40) == "MEDIUM"
    assert map_risk_label(0.39) == "LOW"


def test_decide_signal_rules() -> None:
    assert decide_signal(0.03, "LOW") == "BUY"
    assert decide_signal(-0.03, "LOW") == "SELL"
    assert decide_signal(0.01, "HIGH") == "SELL"
    assert decide_signal(0.00, "MEDIUM") == "HOLD"

"""Pydantic schema package."""

from app.schemas.asset import AssetBase, AssetCreate, AssetRead, AssetUpdate
from app.schemas.ai import (
    AIBatchItem,
    AIBatchResponse,
    AIPipelineRequest,
    AIPipelineResponse,
    HMMStateRead,
    PredictionRead,
    SignalRead,
)
from app.schemas.alert import AlertCreate, AlertLogRead, AlertRead
from app.schemas.auth import LoginRequest, RegisterRequest, TokenPayload, TokenResponse
from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioHoldingRead,
    PortfolioOptimisationRead,
    PortfolioOptimizeRequest,
    PortfolioPerformanceRead,
    PortfolioRead,
    PortfolioUpdate,
)
from app.schemas.risk_indicator import (
    RiskIndicatorBatchItem,
    RiskIndicatorBatchResponse,
    RiskIndicatorComputeRequest,
    RiskIndicatorComputeResponse,
    RiskIndicatorRead,
)
from app.schemas.trade import TradeCreate, TradeRead
from app.schemas.user import CurrentUserRead, UserRead

__all__ = [
    "AIBatchItem",
    "AIBatchResponse",
    "AIPipelineRequest",
    "AIPipelineResponse",
    "AlertCreate",
    "AlertLogRead",
    "AlertRead",
    "AssetBase",
    "AssetCreate",
    "AssetRead",
    "AssetUpdate",
    "HMMStateRead",
    "LoginRequest",
    "PortfolioCreate",
    "PortfolioHoldingRead",
    "PortfolioOptimisationRead",
    "PortfolioOptimizeRequest",
    "PortfolioPerformanceRead",
    "PortfolioRead",
    "PortfolioUpdate",
    "PredictionRead",
    "RegisterRequest",
    "RiskIndicatorBatchItem",
    "RiskIndicatorBatchResponse",
    "RiskIndicatorComputeRequest",
    "RiskIndicatorComputeResponse",
    "RiskIndicatorRead",
    "SignalRead",
    "TokenPayload",
    "TokenResponse",
    "TradeCreate",
    "TradeRead",
    "UserRead",
    "CurrentUserRead",
]

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PortfolioCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    initial_capital: Decimal = Decimal("10000.00")
    is_default: bool = False

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = value.strip()
            if not normalized:
                raise ValueError("name must not be blank.")
            return normalized
        return value


class PortfolioUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    is_default: bool | None = None

    @field_validator("name", mode="before")
    @classmethod
    def normalize_optional_name(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = value.strip()
            return normalized or None
        return value


class PortfolioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    portfolio_id: uuid.UUID
    user_id: uuid.UUID
    name: str
    initial_capital: Decimal
    current_cash: Decimal
    created_at: datetime
    is_default: bool


class PortfolioHoldingRead(BaseModel):
    holding_id: uuid.UUID
    portfolio_id: uuid.UUID
    asset_id: uuid.UUID
    symbol: str | None = None
    name: str | None = None
    quantity: Decimal
    avg_buy_price: Decimal
    latest_price: Decimal | None = None
    market_value: Decimal | None = None
    unrealized_pnl: Decimal | None = None
    last_updated: datetime


class PortfolioPerformanceRead(BaseModel):
    portfolio_id: uuid.UUID
    current_cash: Decimal
    holdings_value: Decimal
    total_portfolio_value: Decimal
    initial_capital: Decimal
    total_pnl: Decimal
    return_pct: Decimal | None
    priced_holdings: int
    missing_price_symbols: list[str]


class PortfolioOptimizeRequest(BaseModel):
    iterations: int = Field(default=250, ge=50, le=2000)


class PortfolioOptimisationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    opt_id: uuid.UUID
    portfolio_id: uuid.UUID
    weights: dict[str, float]
    sharpe_ratio: Decimal
    expected_return: Decimal | None
    expected_risk: Decimal | None
    generations_run: int
    created_at: datetime

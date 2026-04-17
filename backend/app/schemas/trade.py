from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.asset import normalize_symbol


class TradeCreate(BaseModel):
    portfolio_id: uuid.UUID
    symbol: str | None = Field(default=None, max_length=20)
    asset_id: uuid.UUID | None = None
    trade_type: str = Field(min_length=3, max_length=4)
    quantity: Decimal

    @model_validator(mode="after")
    def validate_asset_reference(self) -> "TradeCreate":
        if not self.symbol and not self.asset_id:
            raise ValueError("Provide either symbol or asset_id.")
        if self.symbol:
            self.symbol = normalize_symbol(self.symbol)
        self.trade_type = self.trade_type.strip().upper()
        if self.trade_type not in {"BUY", "SELL"}:
            raise ValueError("trade_type must be BUY or SELL.")
        if self.quantity <= 0:
            raise ValueError("quantity must be greater than zero.")
        return self


class TradeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    trade_id: uuid.UUID
    portfolio_id: uuid.UUID
    asset_id: uuid.UUID
    symbol: str | None = None
    trade_type: str
    quantity: Decimal
    executed_price: Decimal
    total_value: Decimal | None
    traded_at: datetime

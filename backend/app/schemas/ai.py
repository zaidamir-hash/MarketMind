from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.risk_indicator import RiskIndicatorRead


class AIPipelineRequest(BaseModel):
    symbol: str | None = Field(default=None, min_length=1, max_length=20)

    @field_validator("symbol", mode="before")
    @classmethod
    def normalize_optional_symbol(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = value.strip().upper()
            return normalized or None
        return value


class HMMStateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    hmm_state_id: uuid.UUID
    asset_id: uuid.UUID
    symbol: str | None = None
    state_label: str
    state_index: int
    probability: Decimal
    detected_at: datetime


class PredictionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    prediction_id: uuid.UUID
    asset_id: uuid.UUID
    symbol: str | None = None
    model_type: str
    predicted_price: Decimal
    confidence: Decimal | None
    predicted_for: datetime
    actual_price: Decimal | None
    created_at: datetime


class SignalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    signal_id: uuid.UUID
    asset_id: uuid.UUID
    symbol: str | None = None
    signal_type: str
    model_source: str
    strength: Decimal
    regime: str | None
    generated_at: datetime


class AIPipelineResponse(BaseModel):
    status: str
    message: str
    symbol: str
    regime: HMMStateRead | None = None
    prediction: PredictionRead | None = None
    risk_indicator: RiskIndicatorRead | None = None
    signal: SignalRead | None = None


class AIBatchItem(BaseModel):
    symbol: str
    status: str
    message: str | None = None


class AIBatchResponse(BaseModel):
    status: str
    message: str
    details: list[AIBatchItem]

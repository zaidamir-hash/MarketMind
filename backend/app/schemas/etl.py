from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.asset import AssetRead


class OnboardAssetRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=20)

    @field_validator("symbol", mode="before")
    @classmethod
    def normalize_symbol_input(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().upper()
        return value


class FetchPricesRequest(BaseModel):
    symbol: str | None = Field(default=None, max_length=20)
    period: str = "5d"
    interval: str = "5m"

    @field_validator("symbol", mode="before")
    @classmethod
    def normalize_optional_symbol(cls, value: object) -> object:
        if isinstance(value, str):
            stripped = value.strip().upper()
            return stripped or None
        return value


class ETLJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: str
    message: str
    symbol: str | None = None
    rows_inserted: int | None = None
    asset: AssetRead | None = None
    details: dict[str, object] | None = None


class ETLBatchItem(BaseModel):
    symbol: str
    status: str
    rows_inserted: int = 0
    message: str | None = None


class ETLBatchResponse(BaseModel):
    status: str
    message: str
    details: list[ETLBatchItem]


class ScraperLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    log_id: uuid.UUID
    job_name: str
    status: str
    rows_inserted: int | None
    error_message: str | None
    started_at: datetime
    finished_at: datetime | None

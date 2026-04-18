from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


VALID_ASSET_TYPES = {"STOCK", "CRYPTO"}


def normalize_symbol(value: str) -> str:
    return value.strip().upper()


class AssetBase(BaseModel):
    name: str | None = Field(default=None, max_length=150)
    asset_type: str | None = Field(default=None, max_length=10)
    exchange: str | None = Field(default=None, max_length=50)
    currency: str | None = Field(default=None, max_length=10)
    is_active: bool | None = None

    @field_validator("name", "exchange", "currency", mode="before")
    @classmethod
    def strip_optional_strings(cls, value: object) -> object:
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None
        return value

    @field_validator("asset_type", mode="before")
    @classmethod
    def validate_asset_type(cls, value: object) -> object:
        if value is None:
            return value
        if isinstance(value, str):
            normalized = value.strip().upper()
            if normalized not in VALID_ASSET_TYPES:
                raise ValueError("asset_type must be STOCK or CRYPTO.")
            return normalized
        return value

    @field_validator("currency", mode="after")
    @classmethod
    def normalize_currency(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return value.upper()


class AssetCreate(AssetBase):
    symbol: str = Field(min_length=1, max_length=20)
    name: str = Field(min_length=1, max_length=150)
    asset_type: str = Field(min_length=1, max_length=10)
    currency: str = Field(default="USD", max_length=10)
    is_active: bool = True

    @field_validator("symbol", mode="before")
    @classmethod
    def normalize_symbol_field(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = normalize_symbol(value)
            if not normalized:
                raise ValueError("symbol must not be blank.")
            return normalized
        return value


class AssetUpdate(AssetBase):
    pass


class AssetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    asset_id: uuid.UUID
    symbol: str
    name: str
    asset_type: str
    exchange: str | None
    currency: str
    is_active: bool
    added_at: datetime


class AssetCatalogOptionRead(BaseModel):
    asset_id: uuid.UUID | None = None
    symbol: str
    display_name: str
    country: str
    is_crypto: bool
    asset_type: str
    exchange: str | None = None
    currency: str
    is_onboarded: bool
    is_active: bool


class AssetCatalogCategoryRead(BaseModel):
    category_id: str
    category_label: str
    country: str
    is_crypto: bool
    options: list[AssetCatalogOptionRead]


class AssetCatalogRead(BaseModel):
    catalog_name: str
    total_categories: int
    total_options: int
    categories: list[AssetCatalogCategoryRead]

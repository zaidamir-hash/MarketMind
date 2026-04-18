from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Asset
from app.schemas.asset import (
    AssetCatalogRead,
    AssetCatalogCategoryRead,
    AssetCatalogOptionRead,
    AssetCreate,
    AssetUpdate,
    normalize_symbol,
)
from app.services.asset_catalog import load_demo_asset_universe


def list_assets(db: Session, active_only: bool = False) -> list[Asset]:
    query = select(Asset).order_by(Asset.symbol.asc())
    if active_only:
        query = query.where(Asset.is_active.is_(True))
    return list(db.scalars(query).all())


def get_asset_by_id(db: Session, asset_id: uuid.UUID) -> Asset | None:
    return db.get(Asset, asset_id)


def get_asset_by_symbol(db: Session, symbol: str) -> Asset | None:
    normalized_symbol = normalize_symbol(symbol)
    return db.scalar(select(Asset).where(Asset.symbol == normalized_symbol))


def create_asset(db: Session, asset_create: AssetCreate) -> Asset:
    normalized_symbol = normalize_symbol(asset_create.symbol)
    existing_asset = get_asset_by_symbol(db, normalized_symbol)
    if existing_asset is not None:
        raise ValueError("Asset symbol already exists.")

    asset = Asset(
        symbol=normalized_symbol,
        name=asset_create.name,
        asset_type=asset_create.asset_type,
        exchange=asset_create.exchange,
        currency=asset_create.currency,
        is_active=asset_create.is_active,
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


def update_asset(db: Session, asset_id: uuid.UUID, asset_update: AssetUpdate) -> Asset | None:
    asset = get_asset_by_id(db, asset_id)
    if asset is None:
        return None

    update_data = asset_update.model_dump(exclude_unset=True)
    for field_name, value in update_data.items():
        setattr(asset, field_name, value)

    db.commit()
    db.refresh(asset)
    return asset


def deactivate_asset(db: Session, asset_id: uuid.UUID) -> Asset | None:
    asset = get_asset_by_id(db, asset_id)
    if asset is None:
        return None

    asset.is_active = False
    db.commit()
    db.refresh(asset)
    return asset


def list_asset_catalog(db: Session) -> AssetCatalogRead:
    catalog = load_demo_asset_universe()
    raw_categories = catalog.get("categories", [])
    symbols = [
        option["symbol"]
        for category in raw_categories
        for option in category.get("options", [])
    ]

    existing_assets = {
        asset.symbol: asset
        for asset in db.scalars(
            select(Asset).where(Asset.symbol.in_(symbols))
        ).all()
    }

    categories: list[AssetCatalogCategoryRead] = []
    for category in raw_categories:
        options: list[AssetCatalogOptionRead] = []
        for option in category.get("options", []):
            asset = existing_assets.get(option["symbol"])
            options.append(
                AssetCatalogOptionRead(
                    asset_id=asset.asset_id if asset is not None else None,
                    symbol=option["symbol"],
                    display_name=asset.name if asset is not None and asset.name else option["display_name"],
                    country=option["country"],
                    is_crypto=option["is_crypto"],
                    asset_type=asset.asset_type if asset is not None else option["asset_type"],
                    exchange=asset.exchange if asset is not None and asset.exchange else option.get("exchange"),
                    currency=asset.currency if asset is not None else option["currency"],
                    is_onboarded=asset is not None,
                    is_active=bool(asset.is_active) if asset is not None else False,
                )
            )

        categories.append(
            AssetCatalogCategoryRead(
                category_id=category["category_id"],
                category_label=category["category_label"],
                country=category["country"],
                is_crypto=category["is_crypto"],
                options=options,
            )
        )

    return AssetCatalogRead(
        catalog_name=catalog.get("catalog_name", "MarketMind Demo Asset Universe"),
        total_categories=len(categories),
        total_options=sum(len(category.options) for category in categories),
        categories=categories,
    )

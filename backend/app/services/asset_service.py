from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Asset
from app.schemas.asset import AssetCreate, AssetUpdate, normalize_symbol


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

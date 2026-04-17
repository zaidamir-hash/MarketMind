from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.session import get_db
from app.dependencies.auth import get_current_active_user
from app.schemas.asset import AssetCreate, AssetRead, AssetUpdate
from app.services.asset_service import (
    create_asset,
    deactivate_asset,
    get_asset_by_id,
    get_asset_by_symbol,
    list_assets,
    update_asset,
)


router = APIRouter(prefix="/assets", tags=["Assets"])


@router.get("", response_model=list[AssetRead])
def read_assets(
    active_only: bool = Query(default=False),
    db: Session = Depends(get_db),
) -> list[AssetRead]:
    assets = list_assets(db, active_only=active_only)
    return [AssetRead.model_validate(asset) for asset in assets]


@router.get("/active", response_model=list[AssetRead])
def read_active_assets(db: Session = Depends(get_db)) -> list[AssetRead]:
    assets = list_assets(db, active_only=True)
    return [AssetRead.model_validate(asset) for asset in assets]


@router.get("/symbol/{symbol}", response_model=AssetRead)
def read_asset_by_symbol(symbol: str, db: Session = Depends(get_db)) -> AssetRead:
    asset = get_asset_by_symbol(db, symbol)
    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found.",
        )
    return AssetRead.model_validate(asset)


@router.get("/{asset_id}", response_model=AssetRead)
def read_asset_by_id(asset_id: uuid.UUID, db: Session = Depends(get_db)) -> AssetRead:
    asset = get_asset_by_id(db, asset_id)
    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found.",
        )
    return AssetRead.model_validate(asset)


@router.post("", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
def create_asset_route(
    asset_create: AssetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AssetRead:
    _ = current_user
    try:
        asset = create_asset(db, asset_create)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    return AssetRead.model_validate(asset)


@router.patch("/{asset_id}", response_model=AssetRead)
def update_asset_route(
    asset_id: uuid.UUID,
    asset_update: AssetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AssetRead:
    _ = current_user
    asset = update_asset(db, asset_id, asset_update)
    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found.",
        )
    return AssetRead.model_validate(asset)


@router.delete("/{asset_id}", response_model=AssetRead)
def deactivate_asset_route(
    asset_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AssetRead:
    _ = current_user
    asset = deactivate_asset(db, asset_id)
    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found.",
        )
    return AssetRead.model_validate(asset)

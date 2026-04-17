from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Alert, AlertLog, Asset, User
from app.schemas.alert import AlertCreate
from app.services.asset_service import get_asset_by_id, get_asset_by_symbol


def _resolve_alert_asset(db: Session, data: AlertCreate) -> Asset:
    asset = None
    if data.asset_id is not None:
        asset = get_asset_by_id(db, data.asset_id)
    elif data.symbol is not None:
        asset = get_asset_by_symbol(db, data.symbol)

    if asset is None:
        raise ValueError("Asset not found.")
    return asset


def create_alert(db: Session, current_user: User, data: AlertCreate) -> Alert:
    asset = _resolve_alert_asset(db, data)
    alert = Alert(
        user_id=current_user.user_id,
        asset_id=asset.asset_id,
        condition=data.condition,
        threshold=data.threshold,
        is_active=True,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def list_user_alerts(db: Session, current_user: User, active_only: bool = False) -> list[tuple[Alert, str]]:
    statement = (
        select(Alert, Asset.symbol)
        .join(Asset, Asset.asset_id == Alert.asset_id)
        .where(Alert.user_id == current_user.user_id)
        .order_by(Alert.created_at.desc(), Alert.alert_id.desc())
    )
    if active_only:
        statement = statement.where(Alert.is_active.is_(True))

    return list(db.execute(statement).all())


def deactivate_alert(db: Session, current_user: User, alert_id: uuid.UUID) -> tuple[Alert, str] | None:
    row = db.execute(
        select(Alert, Asset.symbol)
        .join(Asset, Asset.asset_id == Alert.asset_id)
        .where(
            Alert.alert_id == alert_id,
            Alert.user_id == current_user.user_id,
        )
        .limit(1)
    ).first()
    if row is None:
        return None

    alert, symbol = row
    alert.is_active = False
    db.commit()
    db.refresh(alert)
    return alert, symbol


def list_user_alert_logs(
    db: Session,
    current_user: User,
    limit: int = 50,
) -> list[tuple[AlertLog, str]]:
    safe_limit = max(1, min(limit, 100))
    return list(
        db.execute(
            select(AlertLog, Asset.symbol)
            .join(Alert, Alert.alert_id == AlertLog.alert_id)
            .join(Asset, Asset.asset_id == Alert.asset_id)
            .where(Alert.user_id == current_user.user_id)
            .order_by(AlertLog.fired_at.desc(), AlertLog.log_id.desc())
            .limit(safe_limit)
        ).all()
    )

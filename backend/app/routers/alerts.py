from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.session import get_db
from app.dependencies.auth import get_current_active_user
from app.schemas.alert import AlertCreate, AlertLogRead, AlertRead
from app.services.asset_service import get_asset_by_id
from app.services.alert_service import create_alert, deactivate_alert, list_user_alert_logs, list_user_alerts


router = APIRouter(prefix="/alerts", tags=["Alerts"])


def _to_alert_read(alert: object, symbol: str | None = None) -> AlertRead:
    payload = AlertRead.model_validate(alert).model_dump()
    payload["symbol"] = symbol
    return AlertRead(**payload)


def _to_alert_log_read(log: object, symbol: str | None = None) -> AlertLogRead:
    payload = AlertLogRead.model_validate(log).model_dump()
    payload["symbol"] = symbol
    return AlertLogRead(**payload)


@router.post("", response_model=AlertRead, status_code=status.HTTP_201_CREATED)
def create_alert_route(
    request: AlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AlertRead:
    try:
        alert = create_alert(db, current_user, request)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    asset = get_asset_by_id(db, alert.asset_id)
    symbol = asset.symbol if asset is not None else request.symbol
    return _to_alert_read(alert, symbol)


@router.get("/logs", response_model=list[AlertLogRead])
def read_alert_logs(
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[AlertLogRead]:
    rows = list_user_alert_logs(db, current_user, limit=limit)
    return [_to_alert_log_read(log, symbol) for log, symbol in rows]


@router.get("", response_model=list[AlertRead])
def read_alerts(
    active_only: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[AlertRead]:
    rows = list_user_alerts(db, current_user, active_only=active_only)
    return [_to_alert_read(alert, symbol) for alert, symbol in rows]


@router.patch("/{alert_id}/deactivate", response_model=AlertRead)
def deactivate_alert_route(
    alert_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AlertRead:
    row = deactivate_alert(db, current_user, alert_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found.")
    alert, symbol = row
    return _to_alert_read(alert, symbol)


@router.delete("/{alert_id}", response_model=AlertRead)
def delete_alert_route(
    alert_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AlertRead:
    row = deactivate_alert(db, current_user, alert_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found.")
    alert, symbol = row
    return _to_alert_read(alert, symbol)

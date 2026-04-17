from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.session import get_db
from app.dependencies.auth import get_current_active_user
from app.schemas.trade import TradeCreate, TradeRead
from app.services.trade_service import create_trade, get_trade, list_trades_for_portfolio


router = APIRouter(prefix="/trades", tags=["Trades"])


def _to_trade_read(trade: object, symbol: str | None = None) -> TradeRead:
    payload = TradeRead.model_validate(trade).model_dump()
    payload["symbol"] = symbol
    return TradeRead(**payload)


@router.post("", response_model=TradeRead, status_code=status.HTTP_201_CREATED)
def create_trade_route(
    request: TradeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> TradeRead:
    try:
        trade = create_trade(db, current_user, request)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    row = get_trade(db, current_user, trade.trade_id)
    if row is None:
        return _to_trade_read(trade, request.symbol)
    refreshed_trade, symbol = row
    return _to_trade_read(refreshed_trade, symbol)


@router.get("/portfolio/{portfolio_id}", response_model=list[TradeRead])
def read_trades_for_portfolio(
    portfolio_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[TradeRead]:
    try:
        rows = list_trades_for_portfolio(db, current_user, portfolio_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return [_to_trade_read(trade, symbol) for trade, symbol in rows]


@router.get("/{trade_id}", response_model=TradeRead)
def read_trade(
    trade_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> TradeRead:
    row = get_trade(db, current_user, trade_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trade not found.")
    trade, symbol = row
    return _to_trade_read(trade, symbol)

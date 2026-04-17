from __future__ import annotations

import uuid
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.models import Asset, Portfolio, PortfolioHolding, PriceHistory, Trade, User
from app.schemas.trade import TradeCreate
from app.services.asset_service import get_asset_by_id, get_asset_by_symbol
from app.services.portfolio_service import get_user_portfolio


def _quantize_money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _get_latest_price_for_asset(db: Session, asset_id: uuid.UUID) -> Decimal | None:
    return db.scalar(
        select(PriceHistory.close_price)
        .where(PriceHistory.asset_id == asset_id)
        .order_by(PriceHistory.recorded_at.desc())
        .limit(1)
    )


def _resolve_trade_asset(db: Session, data: TradeCreate) -> Asset:
    asset = None
    if data.asset_id is not None:
        asset = get_asset_by_id(db, data.asset_id)
    elif data.symbol is not None:
        asset = get_asset_by_symbol(db, data.symbol)

    if asset is None:
        raise ValueError("Asset not found.")
    return asset


def create_trade(db: Session, current_user: User, data: TradeCreate) -> Trade:
    portfolio = get_user_portfolio(db, current_user, data.portfolio_id)
    if portfolio is None:
        raise ValueError("Portfolio not found.")

    asset = _resolve_trade_asset(db, data)
    latest_price = _get_latest_price_for_asset(db, asset.asset_id)
    if latest_price is None:
        raise ValueError("No latest price found for this asset. Run yfinance ETL first.")

    estimated_total = _quantize_money(data.quantity * latest_price)
    if data.trade_type == "BUY" and portfolio.current_cash < estimated_total:
        raise ValueError("Insufficient current_cash for this BUY trade.")

    if data.trade_type == "SELL":
        holding_quantity = db.scalar(
            select(PortfolioHolding.quantity).where(
                PortfolioHolding.portfolio_id == portfolio.portfolio_id,
                PortfolioHolding.asset_id == asset.asset_id,
            )
        )
        held_quantity = holding_quantity or Decimal("0")
        if held_quantity < data.quantity:
            raise ValueError("SELL quantity exceeds held quantity for this asset.")

    trade = Trade(
        portfolio_id=portfolio.portfolio_id,
        asset_id=asset.asset_id,
        trade_type=data.trade_type,
        quantity=data.quantity,
        executed_price=latest_price,
    )
    db.add(trade)

    try:
        db.commit()
        db.refresh(trade)
        return trade
    except SQLAlchemyError as exc:
        db.rollback()
        detail = str(getattr(exc, "orig", exc))
        raise ValueError(detail) from exc


def list_trades_for_portfolio(
    db: Session,
    current_user: User,
    portfolio_id: uuid.UUID,
) -> list[tuple[Trade, str]]:
    portfolio = get_user_portfolio(db, current_user, portfolio_id)
    if portfolio is None:
        raise ValueError("Portfolio not found.")

    return list(
        db.execute(
            select(Trade, Asset.symbol)
            .join(Asset, Asset.asset_id == Trade.asset_id)
            .where(Trade.portfolio_id == portfolio_id)
            .order_by(Trade.traded_at.desc(), Trade.trade_id.desc())
        ).all()
    )


def get_trade(
    db: Session,
    current_user: User,
    trade_id: uuid.UUID,
) -> tuple[Trade, str] | None:
    return db.execute(
        select(Trade, Asset.symbol)
        .join(Asset, Asset.asset_id == Trade.asset_id)
        .join(Portfolio, Portfolio.portfolio_id == Trade.portfolio_id)
        .where(
            Trade.trade_id == trade_id,
            Portfolio.user_id == current_user.user_id,
        )
        .limit(1)
    ).first()

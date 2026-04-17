from __future__ import annotations

import uuid
from decimal import Decimal, ROUND_HALF_UP

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.portfolio_optimizer import build_returns_matrix, optimize_portfolio_weights
from app.db.models import Asset, Portfolio, PortfolioHolding, PortfolioOptimisation, PriceHistory, User
from app.schemas.portfolio import PortfolioCreate, PortfolioHoldingRead, PortfolioUpdate

PREFERRED_OPTIMIZATION_INTERVALS = ("1d", "1h", "5min")


def _quantize_money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _get_latest_price(db: Session, asset_id: uuid.UUID) -> Decimal | None:
    return db.scalar(
        select(PriceHistory.close_price)
        .where(PriceHistory.asset_id == asset_id)
        .order_by(PriceHistory.recorded_at.desc())
        .limit(1)
    )


def _unset_other_defaults(db: Session, user_id: uuid.UUID, keep_portfolio_id: uuid.UUID | None = None) -> None:
    portfolios = list(
        db.scalars(
            select(Portfolio).where(
                Portfolio.user_id == user_id,
                Portfolio.is_default.is_(True),
            )
        ).all()
    )
    for portfolio in portfolios:
        if keep_portfolio_id is not None and portfolio.portfolio_id == keep_portfolio_id:
            continue
        portfolio.is_default = False


def create_portfolio(db: Session, current_user: User, data: PortfolioCreate) -> Portfolio:
    if data.is_default:
        _unset_other_defaults(db, current_user.user_id)

    portfolio = Portfolio(
        user_id=current_user.user_id,
        name=data.name,
        initial_capital=data.initial_capital,
        current_cash=data.initial_capital,
        is_default=data.is_default,
    )
    db.add(portfolio)
    db.commit()
    db.refresh(portfolio)
    return portfolio


def list_user_portfolios(db: Session, current_user: User) -> list[Portfolio]:
    return list(
        db.scalars(
            select(Portfolio)
            .where(Portfolio.user_id == current_user.user_id)
            .order_by(Portfolio.is_default.desc(), Portfolio.created_at.asc())
        ).all()
    )


def get_user_portfolio(db: Session, current_user: User, portfolio_id: uuid.UUID) -> Portfolio | None:
    return db.scalar(
        select(Portfolio).where(
            Portfolio.portfolio_id == portfolio_id,
            Portfolio.user_id == current_user.user_id,
        )
    )


def update_user_portfolio(
    db: Session,
    current_user: User,
    portfolio_id: uuid.UUID,
    data: PortfolioUpdate,
) -> Portfolio | None:
    portfolio = get_user_portfolio(db, current_user, portfolio_id)
    if portfolio is None:
        return None

    update_data = data.model_dump(exclude_unset=True)
    if update_data.get("is_default") is True:
        _unset_other_defaults(db, current_user.user_id, keep_portfolio_id=portfolio_id)

    for field_name, value in update_data.items():
        setattr(portfolio, field_name, value)

    db.commit()
    db.refresh(portfolio)
    return portfolio


def get_portfolio_holdings(
    db: Session,
    current_user: User,
    portfolio_id: uuid.UUID,
) -> list[PortfolioHoldingRead]:
    portfolio = get_user_portfolio(db, current_user, portfolio_id)
    if portfolio is None:
        raise ValueError("Portfolio not found.")

    rows = list(
        db.execute(
            select(PortfolioHolding, Asset.symbol, Asset.name)
            .join(Asset, Asset.asset_id == PortfolioHolding.asset_id)
            .where(
                PortfolioHolding.portfolio_id == portfolio_id,
                PortfolioHolding.quantity > 0,
            )
            .order_by(Asset.symbol.asc())
        ).all()
    )

    holdings: list[PortfolioHoldingRead] = []
    for holding, symbol, name in rows:
        latest_price = _get_latest_price(db, holding.asset_id)
        market_value = None
        unrealized_pnl = None
        if latest_price is not None:
            market_value = _quantize_money(holding.quantity * latest_price)
            unrealized_pnl = _quantize_money(
                (latest_price - holding.avg_buy_price) * holding.quantity
            )

        holdings.append(
            PortfolioHoldingRead(
                holding_id=holding.holding_id,
                portfolio_id=holding.portfolio_id,
                asset_id=holding.asset_id,
                symbol=symbol,
                name=name,
                quantity=holding.quantity,
                avg_buy_price=holding.avg_buy_price,
                latest_price=latest_price,
                market_value=market_value,
                unrealized_pnl=unrealized_pnl,
                last_updated=holding.last_updated,
            )
        )
    return holdings


def get_portfolio_performance(
    db: Session,
    current_user: User,
    portfolio_id: uuid.UUID,
) -> dict[str, object]:
    portfolio = get_user_portfolio(db, current_user, portfolio_id)
    if portfolio is None:
        raise ValueError("Portfolio not found.")

    holdings = get_portfolio_holdings(db, current_user, portfolio_id)
    holdings_value = Decimal("0.00")
    priced_holdings = 0
    missing_price_symbols: list[str] = []

    for holding in holdings:
        if holding.market_value is not None:
            holdings_value += holding.market_value
            priced_holdings += 1
        elif holding.symbol:
            missing_price_symbols.append(holding.symbol)

    total_portfolio_value = _quantize_money(portfolio.current_cash + holdings_value)
    total_pnl = _quantize_money(total_portfolio_value - portfolio.initial_capital)
    return_pct = None
    if portfolio.initial_capital != 0:
        return_pct = (total_pnl / portfolio.initial_capital).quantize(
            Decimal("0.0001"),
            rounding=ROUND_HALF_UP,
        )

    return {
        "portfolio_id": portfolio.portfolio_id,
        "current_cash": portfolio.current_cash,
        "holdings_value": _quantize_money(holdings_value),
        "total_portfolio_value": total_portfolio_value,
        "initial_capital": portfolio.initial_capital,
        "total_pnl": total_pnl,
        "return_pct": return_pct,
        "priced_holdings": priced_holdings,
        "missing_price_symbols": missing_price_symbols,
    }


def _get_optimization_price_series(
    db: Session,
    asset_id: uuid.UUID,
) -> pd.Series | None:
    for interval in PREFERRED_OPTIMIZATION_INTERVALS:
        rows = list(
            db.execute(
                select(PriceHistory.recorded_at, PriceHistory.close_price)
                .where(
                    PriceHistory.asset_id == asset_id,
                    PriceHistory.interval == interval,
                )
                .order_by(PriceHistory.recorded_at.desc())
                .limit(180)
            ).all()
        )
        if len(rows) < 30:
            continue

        rows.reverse()
        index = [recorded_at for recorded_at, _ in rows]
        values = [float(close_price) for _, close_price in rows]
        return pd.Series(values, index=index)

    return None


def run_portfolio_optimization(
    db: Session,
    current_user: User,
    portfolio_id: uuid.UUID,
    *,
    iterations: int = 250,
) -> PortfolioOptimisation:
    portfolio = get_user_portfolio(db, current_user, portfolio_id)
    if portfolio is None:
        raise ValueError("Portfolio not found.")

    rows = list(
        db.execute(
            select(PortfolioHolding, Asset.symbol)
            .join(Asset, Asset.asset_id == PortfolioHolding.asset_id)
            .where(
                PortfolioHolding.portfolio_id == portfolio_id,
                PortfolioHolding.quantity > 0,
            )
            .order_by(Asset.symbol.asc())
        ).all()
    )

    price_series_by_symbol: dict[str, pd.Series] = {}
    for holding, symbol in rows:
        series = _get_optimization_price_series(db, holding.asset_id)
        if series is not None:
            price_series_by_symbol[symbol] = series

    if len(price_series_by_symbol) < 2:
        raise ValueError("Portfolio needs at least 2 held assets with price history to optimize.")

    returns_matrix = build_returns_matrix(price_series_by_symbol)
    optimization_result = optimize_portfolio_weights(returns_matrix, iterations=iterations)

    optimisation = PortfolioOptimisation(
        portfolio_id=portfolio_id,
        weights=optimization_result["weights"],
        sharpe_ratio=optimization_result["sharpe_ratio"],
        expected_return=optimization_result["expected_return"],
        expected_risk=optimization_result["expected_risk"],
        generations_run=optimization_result["generations_run"],
    )
    db.add(optimisation)
    db.commit()
    db.refresh(optimisation)
    return optimisation


def list_portfolio_optimisations(
    db: Session,
    current_user: User,
    portfolio_id: uuid.UUID,
) -> list[PortfolioOptimisation]:
    portfolio = get_user_portfolio(db, current_user, portfolio_id)
    if portfolio is None:
        raise ValueError("Portfolio not found.")

    return list(
        db.scalars(
            select(PortfolioOptimisation)
            .where(PortfolioOptimisation.portfolio_id == portfolio_id)
            .order_by(PortfolioOptimisation.created_at.desc())
        ).all()
    )

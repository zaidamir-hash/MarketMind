from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.session import get_db
from app.dependencies.auth import get_current_active_user
from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioHoldingRead,
    PortfolioOptimisationRead,
    PortfolioOptimizeRequest,
    PortfolioPerformanceRead,
    PortfolioRead,
    PortfolioUpdate,
)
from app.services.portfolio_service import (
    create_portfolio,
    get_portfolio_holdings,
    get_portfolio_performance,
    get_user_portfolio,
    list_portfolio_optimisations,
    list_user_portfolios,
    run_portfolio_optimization,
    update_user_portfolio,
)


router = APIRouter(prefix="/portfolios", tags=["Portfolios"])


@router.post("", response_model=PortfolioRead, status_code=status.HTTP_201_CREATED)
def create_portfolio_route(
    request: PortfolioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PortfolioRead:
    portfolio = create_portfolio(db, current_user, request)
    return PortfolioRead.model_validate(portfolio)


@router.get("", response_model=list[PortfolioRead])
def read_portfolios(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[PortfolioRead]:
    portfolios = list_user_portfolios(db, current_user)
    return [PortfolioRead.model_validate(portfolio) for portfolio in portfolios]


@router.get("/{portfolio_id}", response_model=PortfolioRead)
def read_portfolio(
    portfolio_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PortfolioRead:
    portfolio = get_user_portfolio(db, current_user, portfolio_id)
    if portfolio is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found.")
    return PortfolioRead.model_validate(portfolio)


@router.patch("/{portfolio_id}", response_model=PortfolioRead)
def update_portfolio_route(
    portfolio_id: uuid.UUID,
    request: PortfolioUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PortfolioRead:
    portfolio = update_user_portfolio(db, current_user, portfolio_id, request)
    if portfolio is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found.")
    return PortfolioRead.model_validate(portfolio)


@router.get("/{portfolio_id}/holdings", response_model=list[PortfolioHoldingRead])
def read_portfolio_holdings(
    portfolio_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[PortfolioHoldingRead]:
    try:
        return get_portfolio_holdings(db, current_user, portfolio_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/{portfolio_id}/performance", response_model=PortfolioPerformanceRead)
def read_portfolio_performance(
    portfolio_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PortfolioPerformanceRead:
    try:
        performance = get_portfolio_performance(db, current_user, portfolio_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return PortfolioPerformanceRead(**performance)


@router.post("/{portfolio_id}/optimize", response_model=PortfolioOptimisationRead)
def optimize_portfolio_route(
    portfolio_id: uuid.UUID,
    request: PortfolioOptimizeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PortfolioOptimisationRead:
    try:
        optimisation = run_portfolio_optimization(
            db,
            current_user,
            portfolio_id,
            iterations=request.iterations,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return PortfolioOptimisationRead.model_validate(optimisation)


@router.get("/{portfolio_id}/optimisations", response_model=list[PortfolioOptimisationRead])
def read_portfolio_optimisations(
    portfolio_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[PortfolioOptimisationRead]:
    try:
        optimisations = list_portfolio_optimisations(db, current_user, portfolio_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return [PortfolioOptimisationRead.model_validate(row) for row in optimisations]

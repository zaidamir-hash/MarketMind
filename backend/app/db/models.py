"""SQLAlchemy ORM models aligned with MarketMind Database Schema v2."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Computed,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


SCHEMA_NAME = "marketmind"


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("length(trim(username)) > 0", name="chk_users_username_not_blank"),
        CheckConstraint("length(trim(email)) > 0", name="chk_users_email_not_blank"),
        {"schema": SCHEMA_NAME},
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("TRUE"),
    )

    portfolios: Mapped[list["Portfolio"]] = relationship(back_populates="user")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="user")


class Asset(Base):
    __tablename__ = "assets"
    __table_args__ = (
        CheckConstraint("asset_type IN ('STOCK', 'CRYPTO')", name="chk_assets_type"),
        CheckConstraint("length(trim(symbol)) > 0", name="chk_assets_symbol_not_blank"),
        CheckConstraint("length(trim(name)) > 0", name="chk_assets_name_not_blank"),
        Index("idx_assets_symbol", "symbol"),
        {"schema": SCHEMA_NAME},
    )

    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    symbol: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(10), nullable=False)
    exchange: Mapped[str | None] = mapped_column(String(50))
    currency: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        server_default=text("'USD'"),
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("TRUE"),
    )
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )

    price_history: Mapped[list["PriceHistory"]] = relationship(back_populates="asset")
    risk_indicators: Mapped[list["RiskIndicator"]] = relationship(back_populates="asset")
    ai_predictions: Mapped[list["AIPrediction"]] = relationship(back_populates="asset")
    market_signals: Mapped[list["MarketSignal"]] = relationship(back_populates="asset")
    hmm_states: Mapped[list["HMMState"]] = relationship(back_populates="asset")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="asset")
    portfolio_holdings: Mapped[list["PortfolioHolding"]] = relationship(back_populates="asset")
    trades: Mapped[list["Trade"]] = relationship(back_populates="asset")


class PriceHistory(Base):
    __tablename__ = "price_history"
    __table_args__ = (
        UniqueConstraint("asset_id", "recorded_at", "interval", name="uq_price_asset_time_interval"),
        CheckConstraint(
            "open_price >= 0 AND close_price >= 0 AND high_price >= 0 AND low_price >= 0",
            name="chk_price_non_negative",
        ),
        CheckConstraint("high_price >= low_price", name="chk_price_high_low"),
        CheckConstraint("volume >= 0", name="chk_price_volume_non_negative"),
        CheckConstraint("interval IN ('5min', '1h', '1d')", name="chk_price_interval"),
        Index("idx_price_asset_time", "asset_id", "recorded_at"),
        {"schema": SCHEMA_NAME},
    )

    price_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA_NAME}.assets.asset_id"),
        nullable=False,
    )
    open_price: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    close_price: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    high_price: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    low_price: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    volume: Mapped[int] = mapped_column(BigInteger, nullable=False)
    interval: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        server_default=text("'5min'"),
    )
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    asset: Mapped["Asset"] = relationship(back_populates="price_history")


class Portfolio(Base):
    __tablename__ = "portfolios"
    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name="chk_portfolios_name_not_blank"),
        CheckConstraint("initial_capital >= 0", name="chk_portfolios_initial_capital_positive"),
        CheckConstraint("current_cash >= 0", name="chk_portfolios_current_cash_non_negative"),
        Index("idx_portfolios_user_id", "user_id"),
        {"schema": SCHEMA_NAME},
    )

    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA_NAME}.users.user_id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    initial_capital: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
        server_default=text("10000.00"),
    )
    current_cash: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
        server_default=text("10000.00"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("FALSE"),
    )

    user: Mapped["User"] = relationship(back_populates="portfolios")
    holdings: Mapped[list["PortfolioHolding"]] = relationship(back_populates="portfolio")
    trades: Mapped[list["Trade"]] = relationship(back_populates="portfolio")
    optimisation_runs: Mapped[list["PortfolioOptimisation"]] = relationship(back_populates="portfolio")


class PortfolioHolding(Base):
    __tablename__ = "portfolio_holdings"
    __table_args__ = (
        UniqueConstraint("portfolio_id", "asset_id", name="uq_holdings_portfolio_asset"),
        CheckConstraint("quantity >= 0", name="chk_holdings_quantity_non_negative"),
        CheckConstraint("avg_buy_price >= 0", name="chk_holdings_avg_buy_price_non_negative"),
        Index("idx_holdings_asset_id", "asset_id"),
        {"schema": SCHEMA_NAME},
    )

    holding_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA_NAME}.portfolios.portfolio_id"),
        nullable=False,
    )
    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA_NAME}.assets.asset_id"),
        nullable=False,
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(18, 8),
        nullable=False,
        server_default=text("0"),
    )
    avg_buy_price: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )

    portfolio: Mapped["Portfolio"] = relationship(back_populates="holdings")
    asset: Mapped["Asset"] = relationship(back_populates="portfolio_holdings")


class Trade(Base):
    __tablename__ = "trades"
    __table_args__ = (
        CheckConstraint("trade_type IN ('BUY', 'SELL')", name="chk_trades_type"),
        CheckConstraint("quantity > 0", name="chk_trades_quantity_positive"),
        CheckConstraint("executed_price >= 0", name="chk_trades_executed_price_non_negative"),
        Index("idx_trades_portfolio", "portfolio_id", "traded_at"),
        Index("idx_trades_asset_id", "asset_id"),
        {"schema": SCHEMA_NAME},
    )

    trade_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA_NAME}.portfolios.portfolio_id"),
        nullable=False,
    )
    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA_NAME}.assets.asset_id"),
        nullable=False,
    )
    trade_type: Mapped[str] = mapped_column(String(4), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    executed_price: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    total_value: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 2),
        Computed("ROUND(quantity * executed_price, 2)", persisted=True),
    )
    traded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )

    portfolio: Mapped["Portfolio"] = relationship(back_populates="trades")
    asset: Mapped["Asset"] = relationship(back_populates="trades")


class RiskIndicator(Base):
    __tablename__ = "risk_indicators"
    __table_args__ = (
        CheckConstraint("rsi_14 IS NULL OR rsi_14 BETWEEN 0 AND 100", name="chk_risk_rsi"),
        CheckConstraint(
            "market_cap_cat IS NULL OR market_cap_cat IN ('LARGE', 'MID', 'SMALL', 'MICRO')",
            name="chk_risk_market_cap_cat",
        ),
        CheckConstraint("volatility_label IN ('HIGH', 'MEDIUM', 'LOW')", name="chk_risk_volatility_label"),
        CheckConstraint(
            "momentum_label IN ('BULLISH', 'NEUTRAL', 'BEARISH')",
            name="chk_risk_momentum_label",
        ),
        CheckConstraint("volume_label IN ('SURGE', 'NORMAL', 'LOW')", name="chk_risk_volume_label"),
        CheckConstraint("risk_score IS NULL OR risk_score BETWEEN 0 AND 1", name="chk_risk_score"),
        CheckConstraint("risk_label IS NULL OR risk_label IN ('HIGH', 'MEDIUM', 'LOW')", name="chk_risk_label"),
        CheckConstraint("volatility_30d >= 0", name="chk_risk_volatility_non_negative"),
        CheckConstraint("volume_ratio >= 0", name="chk_risk_volume_ratio_non_negative"),
        CheckConstraint("price_vs_52w_high >= 0", name="chk_risk_price_vs_52w_high_range"),
        Index("idx_risk_asset_time", "asset_id", "computed_at"),
        {"schema": SCHEMA_NAME},
    )

    risk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA_NAME}.assets.asset_id"),
        nullable=False,
    )
    beta: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    volatility_30d: Mapped[Decimal] = mapped_column(Numeric(8, 6), nullable=False)
    rsi_14: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    volume_ratio: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False)
    price_vs_52w_high: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False)
    price_vs_sma50: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False)
    market_cap_cat: Mapped[str | None] = mapped_column(String(10))
    volatility_label: Mapped[str] = mapped_column(String(10), nullable=False)
    momentum_label: Mapped[str] = mapped_column(String(10), nullable=False)
    volume_label: Mapped[str] = mapped_column(String(10), nullable=False)
    risk_score: Mapped[Decimal | None] = mapped_column(Numeric(6, 4))
    risk_label: Mapped[str | None] = mapped_column(String(10))
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )

    asset: Mapped["Asset"] = relationship(back_populates="risk_indicators")


class AIPrediction(Base):
    __tablename__ = "ai_predictions"
    __table_args__ = (
        CheckConstraint("length(trim(model_type)) > 0", name="chk_predictions_model_type_not_blank"),
        CheckConstraint("predicted_price >= 0", name="chk_predictions_predicted_price_non_negative"),
        CheckConstraint(
            "actual_price IS NULL OR actual_price >= 0",
            name="chk_predictions_actual_price_non_negative",
        ),
        CheckConstraint("confidence IS NULL OR confidence BETWEEN 0 AND 1", name="chk_predictions_confidence"),
        Index("idx_pred_asset_model", "asset_id", "model_type"),
        {"schema": SCHEMA_NAME},
    )

    prediction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA_NAME}.assets.asset_id"),
        nullable=False,
    )
    model_type: Mapped[str] = mapped_column(String(30), nullable=False)
    predicted_price: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    predicted_for: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    actual_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )

    asset: Mapped["Asset"] = relationship(back_populates="ai_predictions")


class MarketSignal(Base):
    __tablename__ = "market_signals"
    __table_args__ = (
        CheckConstraint("signal_type IN ('BUY', 'SELL', 'HOLD')", name="chk_signals_type"),
        CheckConstraint("strength BETWEEN 0 AND 1", name="chk_signals_strength"),
        CheckConstraint("length(trim(model_source)) > 0", name="chk_signals_model_source_not_blank"),
        CheckConstraint(
            "regime IS NULL OR regime IN ('BULL', 'BEAR', 'SIDEWAYS')",
            name="chk_signals_regime",
        ),
        Index("idx_signals_asset", "asset_id", "generated_at"),
        {"schema": SCHEMA_NAME},
    )

    signal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA_NAME}.assets.asset_id"),
        nullable=False,
    )
    signal_type: Mapped[str] = mapped_column(String(10), nullable=False)
    model_source: Mapped[str] = mapped_column(String(30), nullable=False)
    strength: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    regime: Mapped[str | None] = mapped_column(String(10))
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )

    asset: Mapped["Asset"] = relationship(back_populates="market_signals")


class HMMState(Base):
    __tablename__ = "hmm_states"
    __table_args__ = (
        CheckConstraint("state_label IN ('BULL', 'BEAR', 'SIDEWAYS')", name="chk_hmm_state_label"),
        CheckConstraint("state_index IN (0, 1, 2)", name="chk_hmm_state_index"),
        CheckConstraint("probability BETWEEN 0 AND 1", name="chk_hmm_probability"),
        Index("idx_hmm_asset_time", "asset_id", "detected_at"),
        {"schema": SCHEMA_NAME},
    )

    hmm_state_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA_NAME}.assets.asset_id"),
        nullable=False,
    )
    state_label: Mapped[str] = mapped_column(String(10), nullable=False)
    state_index: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    probability: Mapped[Decimal] = mapped_column(Numeric(6, 5), nullable=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    asset: Mapped["Asset"] = relationship(back_populates="hmm_states")


class PortfolioOptimisation(Base):
    __tablename__ = "portfolio_optimisation"
    __table_args__ = (
        CheckConstraint("jsonb_typeof(weights) = 'object'", name="chk_optimisation_weights_object"),
        CheckConstraint("generations_run > 0", name="chk_optimisation_generations_positive"),
        CheckConstraint(
            "expected_risk IS NULL OR expected_risk >= 0",
            name="chk_optimisation_expected_risk_non_negative",
        ),
        Index("idx_optimisation_portfolio_id", "portfolio_id"),
        {"schema": SCHEMA_NAME},
    )

    opt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA_NAME}.portfolios.portfolio_id"),
        nullable=False,
    )
    weights: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    sharpe_ratio: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False)
    expected_return: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    expected_risk: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    generations_run: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )

    portfolio: Mapped["Portfolio"] = relationship(back_populates="optimisation_runs")


class Alert(Base):
    __tablename__ = "alerts"
    __table_args__ = (
        CheckConstraint("condition IN ('ABOVE', 'BELOW')", name="chk_alerts_condition"),
        CheckConstraint("threshold >= 0", name="chk_alerts_threshold_non_negative"),
        Index("idx_alerts_user_id", "user_id"),
        Index("idx_alerts_asset_id", "asset_id"),
        Index(
            "idx_alerts_active",
            "is_active",
            postgresql_where=text("is_active = TRUE"),
        ),
        {"schema": SCHEMA_NAME},
    )

    alert_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA_NAME}.users.user_id"),
        nullable=False,
    )
    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA_NAME}.assets.asset_id"),
        nullable=False,
    )
    condition: Mapped[str] = mapped_column(String(10), nullable=False)
    threshold: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("TRUE"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )

    user: Mapped["User"] = relationship(back_populates="alerts")
    asset: Mapped["Asset"] = relationship(back_populates="alerts")
    logs: Mapped[list["AlertLog"]] = relationship(back_populates="alert")


class AlertLog(Base):
    __tablename__ = "alert_logs"
    __table_args__ = (
        CheckConstraint("triggered_price >= 0", name="chk_alert_logs_triggered_price_non_negative"),
        Index("idx_alert_logs_alert_id", "alert_id"),
        {"schema": SCHEMA_NAME},
    )

    log_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    alert_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA_NAME}.alerts.alert_id"),
        nullable=False,
    )
    triggered_price: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    fired_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )

    alert: Mapped["Alert"] = relationship(back_populates="logs")


class ScraperLog(Base):
    __tablename__ = "scraper_logs"
    __table_args__ = (
        CheckConstraint("status IN ('SUCCESS', 'FAIL')", name="chk_scraper_status"),
        CheckConstraint("rows_inserted IS NULL OR rows_inserted >= 0", name="chk_scraper_rows_inserted_non_negative"),
        CheckConstraint("length(trim(job_name)) > 0", name="chk_scraper_job_name_not_blank"),
        CheckConstraint(
            "finished_at IS NULL OR finished_at >= started_at",
            name="chk_scraper_finished_after_started",
        ),
        Index("idx_scraper_logs_job_time", "job_name", "started_at"),
        {"schema": SCHEMA_NAME},
    )

    log_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    job_name: Mapped[str] = mapped_column(String(60), nullable=False)
    status: Mapped[str] = mapped_column(String(10), nullable=False)
    rows_inserted: Mapped[int | None] = mapped_column(Integer)
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

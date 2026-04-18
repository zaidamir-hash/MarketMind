# Architecture Overview

MarketMind is a local-only monorepo with a React frontend, a FastAPI backend, and a PostgreSQL database built strictly on Schema v2.

## Frontend

- Location: `frontend/`
- Stack: React + Vite, JavaScript only
- Responsibilities:
  - register/login flows
  - dashboard summaries
  - assets, ETL, risk, AI, portfolio, trade, and alert pages
  - token-aware API calls through `src/services/`

The frontend talks to the backend over HTTP and uses Bearer tokens for protected actions.

## Backend

- Location: `backend/`
- Stack: FastAPI, SQLAlchemy 2.0, Pydantic
- Responsibilities:
  - JWT authentication
  - CRUD and workflow APIs
  - ETL and analytics entrypoints
  - portfolio/trade/alert business workflows
  - local-only CORS configuration for the frontend

Routers currently included in the app:

- `health`
- `auth`
- `assets`
- `etl`
- `risk_indicators`
- `ai`
- `portfolios`
- `trades`
- `alerts`

## Database

- Location: `database/marketmind_schema_v2_postgresql.sql`
- Engine: PostgreSQL
- Schema name: `marketmind`
- Scope:
  - 14 base tables
  - 4 materialized views
  - 6 triggers

The executable SQL file is the only schema definition. The application does not create or migrate tables.

## yfinance ETL

ETL runs from backend modules and manual API/CLI entrypoints.

It is used only for:

- asset metadata
- OHLCV price history
- beta
- market-cap source data
- historical windows for risk feature calculations

It writes to:

- `assets`
- `price_history`
- `scraper_logs`

## Risk Indicators

The risk pipeline computes deterministic features from market data and stores them in `risk_indicators`.

Current computed fields include:

- `volatility_30d`
- `rsi_14`
- `volume_ratio`
- `price_vs_52w_high`
- `price_vs_sma50`
- `beta` when available
- deterministic volatility, momentum, and volume labels

## AI Pipeline

The AI layer is intentionally simple and demo-friendly.

It currently produces:

- HMM-style market regimes into `hmm_states`
- linear-regression price predictions into `ai_predictions`
- rule-based trading signals into `market_signals`
- simplified Bayesian-style risk scoring updates on `risk_indicators`

## Portfolio, Trade, Alert, and Optimizer Flow

- Portfolios are user-scoped.
- Trades insert into `trades` only.
- Database triggers update:
  - `portfolio_holdings`
  - `portfolios.current_cash`
  - `alert_logs`
  - `ai_predictions.actual_price`
- Alerts insert into `alerts`; the database creates logs later after qualifying price inserts.
- Portfolio optimization writes to `portfolio_optimisation` using a simple demo-friendly optimizer.

## Materialized Views and Triggers

Schema v2 includes materialized views and triggers to keep important derived data in the database layer.

Key trigger-managed behaviors:

- holdings updates after trades
- cash updates after trades
- alert log creation after price inserts
- prediction actual-price backfill after price inserts

The application should not duplicate those trigger-managed responsibilities in Python.

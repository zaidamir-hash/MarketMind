# Backend

This folder contains the FastAPI backend foundation for MarketMind.

## Current State

- FastAPI backend with local API routes
- Environment-based configuration
- PostgreSQL connection wiring
- Health endpoints
- Real JWT auth endpoints
- Assets API
- yfinance ETL routes and CLI
- Risk indicator pipeline
- Core AI modules
- Portfolio, trade, alert, and optimizer APIs
- Curated 50-option demo asset universe

## Local Run Instructions

1. `cd backend`
2. `python -m venv .venv`
3. `.\.venv\Scripts\activate`
4. `pip install -r requirements.txt`
5. `copy .env.example .env`
6. Edit `DATABASE_URL` and `POSTGRES_PASSWORD` in `.env`
7. `uvicorn app.main:app --reload`
8. Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Health Checks

After starting the server, test:

- `GET /`
- `GET /health`
- `GET /health/db`

## Optional Database Check Script

You can also run:

- `python -m app.db.check_connection`

This script loads backend settings, tests `SELECT 1`, and verifies that the `marketmind` schema exists.

## SQLAlchemy Models

SQLAlchemy models mirror the executable PostgreSQL schema for backend development.

- Run model validation with `python -m app.db.validate_models`
- The schema is still created by `database/marketmind_schema_v2_postgresql.sql` only
- SQLAlchemy does not create or modify database tables in this project

## Auth Testing

Before running auth flows:

- `backend/.env` must contain `DATABASE_URL`
- `backend/.env` must contain `JWT_SECRET_KEY`
- Do not commit `backend/.env`

Run the backend:

1. `cd backend`
2. `.\.venv\Scripts\activate`
3. `pip install -r requirements.txt`
4. `uvicorn app.main:app --reload`

Register a user:

- `POST /auth/register`

Login:

- `POST /auth/login`
- `POST /auth/token` is also available for Swagger OAuth2 flow

Read the current user:

- `GET /auth/me` with `Authorization: Bearer <token>`

## Assets API Testing

This phase adds manual asset CRUD over the existing `assets` table only.

- `GET /assets`
- `GET /assets/active`
- `GET /assets/catalog`
- `GET /assets/symbol/{symbol}`
- `GET /assets/{asset_id}`
- `POST /assets` requires Bearer token
- `PATCH /assets/{asset_id}` requires Bearer token
- `DELETE /assets/{asset_id}` soft-deactivates the asset and requires Bearer token

Notes:

- This phase does not use yfinance yet
- `POST`, `PATCH`, and `DELETE` do not create price history, risk indicators, or any fake market data
- `GET /assets/catalog` exposes the curated 50-option demo universe grouped into 5 categories for frontend dropdowns

## yfinance ETL

Purpose:

- onboard asset metadata from yfinance into `assets`
- fetch OHLCV candles from yfinance into `price_history`
- write ETL execution status to `scraper_logs`

Notes:

- risk indicators are not implemented in this phase
- yfinance field availability can vary by ticker
- this phase does not use yfinance news or any external news source

Protected API endpoints:

- `POST /etl/onboard-asset`
- `POST /etl/fetch-prices`
- `POST /etl/fetch-prices/all-active`
- `GET /etl/logs`

CLI commands:

- `python -m app.etl.run_yfinance_etl onboard AAPL`
- `python -m app.etl.run_yfinance_etl prices AAPL --period 5d --interval 5m`
- `python -m app.etl.run_yfinance_etl prices-all --period 5d --interval 5m`
- `python -m app.etl.bootstrap_demo_universe`

Curated demo bootstrap:

- `python -m app.etl.bootstrap_demo_universe` prepares the curated 50-option demo universe
- It onboards all catalog assets, fetches stored daily and intraday price history, computes risk indicators, and runs the AI pipeline
- The command is safe to rerun, but risk and AI snapshots are append-style records

## Risk Indicators

This phase computes deterministic risk features from yfinance daily market data and inserts them into `risk_indicators`.

Computed fields in this phase:

- `volatility_30d`
- `rsi_14`
- `volume_ratio`
- `price_vs_52w_high`
- `price_vs_sma50`
- `beta` when available from yfinance
- deterministic `volatility_label`, `momentum_label`, and `volume_label`

Not computed in this phase:

- `risk_score` remains `NULL`
- `risk_label` remains `NULL`
- Bayesian/AI risk inference is deferred to the later AI modules phase

Protected API endpoints:

- `POST /risk-indicators/compute`
- `POST /risk-indicators/compute/all-active`

Read endpoints:

- `GET /risk-indicators`
- `GET /risk-indicators/symbol/{symbol}`

CLI commands:

- `python -m app.etl.run_risk_indicators compute AAPL`
- `python -m app.etl.run_risk_indicators compute-all`

Notes:

- yfinance data availability can vary by ticker and runtime connectivity
- insufficient daily history prevents insertion of incomplete risk rows
- this phase does not compute Bayesian `risk_score` or `risk_label`

## AI Modules

This phase adds simple, demo-friendly AI outputs built from stored MarketMind data.

What it does:

- detects a simple HMM-style market regime from stored `price_history`
- creates a simple `LinearRegression` next-price prediction
- updates the latest `risk_indicators` row with a simplified Bayesian-style `risk_score` and `risk_label`
- generates a `BUY`, `HOLD`, or `SELL` market signal

Prerequisites:

- `price_history` rows must already exist for the target asset
- `risk_indicators` rows should already exist before Bayesian-style risk scoring runs

Protected API endpoints:

- `POST /ai/run/{symbol}`
- `POST /ai/run-all`
- `POST /ai/reconcile-actuals`
- `POST /ai/reconcile-actuals/{symbol}`

Read endpoints:

- `GET /ai/predictions`
- `GET /ai/predictions/symbol/{symbol}`
- `GET /ai/signals`
- `GET /ai/signals/symbol/{symbol}`
- `GET /ai/regimes`
- `GET /ai/regimes/symbol/{symbol}`

CLI commands:

- `python -m app.ai.run_ai_pipeline run AAPL`
- `python -m app.ai.run_ai_pipeline run-all`
- `python -m app.etl.run_prediction_actuals reconcile`
- `python -m app.etl.run_prediction_actuals reconcile AAPL`

Notes:

- the AI modules are intentionally simple and stable for demo use
- outputs depend on actual stored market data and will fail clearly if data is missing
- `ai_predictions.actual_price` is filled from real stored `price_history` rows once a prediction has matured
- the database trigger still backfills matching rows on new price inserts, and the backend also reconciles older missed predictions after price ETL or via the manual reconcile commands above
- `GET /ai/predictions` prefers the newest backfilled comparable prediction per asset when one exists; otherwise it falls back to the newest pending prediction row
- if price ETL has not yet fetched a real bar at or after `predicted_for`, `actual_price` remains `NULL` until relevant market data exists
- Genetic Algorithm portfolio optimization is intentionally deferred until portfolio and holding APIs exist

## Portfolio APIs

Protected portfolio endpoints:

- `POST /portfolios`
- `GET /portfolios`
- `GET /portfolios/{portfolio_id}`
- `PATCH /portfolios/{portfolio_id}`
- `GET /portfolios/{portfolio_id}/holdings`
- `GET /portfolios/{portfolio_id}/performance`
- `POST /portfolios/{portfolio_id}/optimize`
- `GET /portfolios/{portfolio_id}/optimisations`

Notes:

- portfolios are user-scoped
- holdings and current cash are managed by database triggers after trade inserts
- run yfinance ETL first so holdings and performance can resolve latest prices

## Trade APIs

Protected trade endpoints:

- `POST /trades`
- `GET /trades/portfolio/{portfolio_id}`
- `GET /trades/{trade_id}`

Notes:

- trades use the latest stored `price_history` close as `executed_price`
- if no stored price exists for an asset, the API returns a clear error telling you to run yfinance ETL first
- the app inserts into `trades` only; the database triggers update holdings and portfolio cash
- the frontend trade form uses category and asset dropdowns sourced from `GET /assets/catalog`, but the backend trade API still accepts the same `symbol` payload

## Alert APIs

Protected alert endpoints:

- `POST /alerts`
- `GET /alerts`
- `GET /alerts/logs`
- `PATCH /alerts/{alert_id}/deactivate`
- `DELETE /alerts/{alert_id}`

Notes:

- creating an alert inserts into `alerts` only
- `alert_logs` are created by the database trigger after matching `price_history` inserts
- deactivation is soft only; alerts are not physically deleted in this phase

## Portfolio Optimization

This phase uses a simple demo-friendly random weight search over held assets with stored `1d` price history.

Requirements:

- the portfolio must hold at least 2 assets
- both assets must have stored `price_history` rows; `1d` is preferred and lower intervals are used as fallback

Notes:

- optimization writes to `portfolio_optimisation`
- holdings, cash, and alert logs remain database-trigger-managed

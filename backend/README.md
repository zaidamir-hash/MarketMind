# Backend

This folder contains the FastAPI backend foundation for MarketMind.

## Current State

- FastAPI app foundation only
- Environment-based configuration
- PostgreSQL connection wiring
- Health endpoints only
- Real JWT auth endpoints
- No business endpoints yet
- No ETL jobs yet
- No AI services yet

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
- `GET /assets/symbol/{symbol}`
- `GET /assets/{asset_id}`
- `POST /assets` requires Bearer token
- `PATCH /assets/{asset_id}` requires Bearer token
- `DELETE /assets/{asset_id}` soft-deactivates the asset and requires Bearer token

Notes:

- This phase does not use yfinance yet
- `POST`, `PATCH`, and `DELETE` do not create price history, risk indicators, or any fake market data

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

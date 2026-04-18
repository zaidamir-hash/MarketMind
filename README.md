# MarketMind

MarketMind is a local-only stock and crypto intelligence platform built for a university demo. The project combines a FastAPI backend, a React frontend, PostgreSQL Schema v2, yfinance-powered market ingestion, deterministic risk analytics, simple AI outputs, and portfolio/trade/alert workflows.

## Current Scope

Implemented layers:

- FastAPI backend with JWT authentication
- Assets API
- Manual yfinance ETL for asset onboarding and price history
- Risk indicator computation
- AI outputs for regimes, predictions, signals, and simplified risk scoring
- Portfolio, trade, alert, and optimizer APIs
- React dashboard and workflow pages

Out of scope by project decision:

- Alembic
- Docker
- TypeScript
- news/sentiment ingestion
- Claude/chat/AI summary features
- schema changes outside Database Schema v2

## Tech Stack

- Frontend: React, Vite, JavaScript, Axios, Recharts
- Backend: FastAPI, SQLAlchemy 2.0, Pydantic
- Database: PostgreSQL
- Data ingestion: yfinance
- Analytics: pandas, numpy, scikit-learn, hmmlearn, pgmpy, DEAP

## Repository Structure

- `database/`
  The executable PostgreSQL schema, verification queries, and seed assets.
- `backend/`
  FastAPI app, ORM models, routers, services, ETL/AI modules, and tests.
- `frontend/`
  React + Vite app with pages, API services, auth handling, and dashboard UI.
- `docs/`
  Project decisions, architecture notes, runbook, and task plan.
- `scripts/`
  Local PowerShell environment check helpers.

## Database Rules

- Schema source of truth: `database/marketmind_schema_v2_postgresql.sql`
- Use executable SQL only
- Do not add Alembic
- Do not add `SENTIMENT_SCORES`, news tables, sentiment tables, Claude tables, or AI summary/chat tables
- Database triggers are responsible for:
  - holdings updates
  - portfolio cash updates
  - alert log creation
  - `ai_predictions.actual_price` backfill

## Local Run Order

1. Run the PostgreSQL schema from `database/marketmind_schema_v2_postgresql.sql`.
2. Verify schema objects with `database/verification_queries.sql`.
3. Optionally seed demo assets with `database/seed_assets.sql`.
4. Start the backend from `backend/`.
5. Start the frontend from `frontend/`.

## Quick Start

Database:

- Run the schema SQL in PostgreSQL
- Use the runbook in [docs/DATABASE_RUNBOOK.md](C:/Users/alize/Desktop/Uni Stuff/AI+DB+SDA Project/docs/DATABASE_RUNBOOK.md)

Backend:

1. `cd backend`
2. `python -m venv .venv`
3. `.\.venv\Scripts\activate`
4. `pip install -r requirements.txt`
5. `copy .env.example .env`
6. Set `DATABASE_URL`, `POSTGRES_PASSWORD`, `JWT_SECRET_KEY`, and `FRONTEND_URL`
7. `uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload`

Frontend:

1. `cd frontend`
2. `copy .env.example .env`
3. `npm.cmd install`
4. `npm.cmd run dev -- --host 127.0.0.1 --port 5173`

Recommended local URLs:

- Frontend: `http://127.0.0.1:5173`
- Backend: `http://127.0.0.1:8000`

## Demo Notes

- ETL and risk recomputation depend on live yfinance availability.
- Portfolio trades require stored prices first.
- Alert logs only appear after a later price insert crosses the alert threshold.
- Portfolio optimization requires at least two held assets with sufficient stored history.

## Important Constraint

MarketMind must stay aligned with Schema v2. Do not add news, sentiment, Claude, AI summary, or extra chat tables unless the project owner explicitly changes the scope.

# MarketMind Codex Instructions

## Project Identity

Project name: MarketMind

MarketMind is a local-only AI-powered stock and crypto intelligence platform for development and demo use.

This file is the single source of truth for project decisions unless I explicitly override something later.

## Core Stack Decisions

- Frontend: React with JavaScript only.
- Do not use TypeScript.
- Backend: FastAPI.
- Database: PostgreSQL.
- Database schema source: use only the executable PostgreSQL SQL schema file.
- Do not set up Alembic migrations unless I explicitly ask later.
- Authentication: implement a real JWT login system.
- Development mode: local-only for now.

## Database Schema Rules

Strictly follow MarketMind Database Schema v2.

The schema has:

- 14 base tables
- 4 materialized views
- 6 triggers
- PostgreSQL schema name: marketmind

Do not invent new tables, replacement schemas, or parallel database structures unless I explicitly approve them.

The current schema does not include the following, and they must not be added:

- SENTIMENT_SCORES
- NEWS_ARTICLES
- AI_SUMMARIES
- Claude chat tables
- any other news tables
- any other sentiment tables

If a requested feature would require schema expansion or conflicts with Schema v2, stop and ask before continuing.

## Database Behavior Rules

Use the existing `marketmind_schema_v2_postgresql.sql` file as the only database schema definition.

Do not manually implement logic that duplicates database trigger behavior when the schema already handles it.

Database triggers handle:

- portfolio holdings updates
- cash updates
- alert log creation
- `ai_predictions.actual_price` backfill

## Backend Rules

Use FastAPI with:

- SQLAlchemy 2.0
- Pydantic schemas
- clear routers
- service layer where useful
- environment variables for configuration
- no hardcoded passwords or secrets

Authentication must be a real JWT login system, not a fake/demo auth stub.

## Frontend Rules

Use:

- React
- Vite
- JavaScript only
- Recharts

Do not introduce TypeScript, TSX, or TypeScript config files.

Keep frontend API calls organized in a `services/api` layer.
Keep the UI clean and demo-friendly.

## AI/Analytics Rules

Use simple, demo-friendly AI implementations.

Prefer lightweight, understandable approaches over overengineered pipelines.

Allowed technologies when needed:

- scikit-learn for regression/classification
- hmmlearn for HMM regimes
- pgmpy for Bayesian risk inference
- DEAP for portfolio optimization
- pandas/numpy for feature computation

Do not introduce heavier AI systems unless I explicitly ask for them.

## yfinance Rules

Use yfinance only for:

- asset metadata
- OHLCV candles
- beta
- market cap
- historical price/volume windows used for risk features

Do not use yfinance for news scraping.
Do not add news ingestion, sentiment ingestion, or related tables.

## Development Rules

Before coding:

1. Inspect existing files.
2. Explain the plan briefly.
3. Do not overwrite working files blindly.
4. Make small, testable changes.
5. Run relevant tests or commands after changes.
6. Show what changed.

## Testing Rules

Add simple tests where practical.
For backend, prefer pytest.
For frontend, prefer basic component/API integration tests if setup exists.

## Important Behavior

If schema ambiguity appears, ask me before continuing.
If a feature is not present in Schema v2, ask before creating anything new.
Do not implement backend, frontend, ETL, or AI features unless requested.

# Project Decisions

This document records the fixed setup decisions for MarketMind. It should stay aligned with `AGENTS.md`.

## Core Decisions

- Project name: MarketMind
- Frontend: React with JavaScript only
- TypeScript is not allowed
- Backend: FastAPI
- Database: local PostgreSQL
- Development mode: local-only

## Database Decisions

- Use Database Schema v2 only
- Use only `database/marketmind_schema_v2_postgresql.sql` as the executable schema source
- Do not add Alembic unless explicitly requested later
- Do not create replacement schemas, parallel schema definitions, or extra migration systems
- The PostgreSQL schema name is `marketmind`

## Restricted Tables and Features

The following must not be added unless explicitly approved later:

- `SENTIMENT_SCORES`
- news tables
- sentiment tables
- Claude tables
- AI summary tables
- AI chat tables

## Authentication Decision

- Authentication is planned as a real JWT login system
- JWT auth is not implemented yet during the setup phase

## AI and Analytics Direction

- AI implementations should remain simple and demo-friendly
- Prefer understandable, lightweight approaches over complex or overengineered systems

## yfinance Usage Rules

yfinance is reserved for:

- asset metadata
- OHLCV candles
- beta
- market cap
- historical price and volume windows used for risk features

yfinance must not be used for:

- news scraping
- sentiment scraping
- any feature that would require extra news or sentiment tables

## Trigger-Handled Database Behavior

Database triggers are responsible for:

- holdings updates
- cash updates
- alert log creation
- `ai_predictions.actual_price` backfill

Application code should not duplicate that trigger-owned behavior later.

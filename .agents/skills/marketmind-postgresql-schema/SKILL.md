---
name: marketmind-postgresql-schema
description: Use when working on MarketMind PostgreSQL schema, SQLAlchemy models, triggers, materialized views, or database validation.
---

Follow MarketMind Database Schema v2 exactly.

Use only the executable PostgreSQL SQL schema file as the schema source of truth.
Do not set up Alembic migrations unless the user explicitly asks for them.

Do not add new tables unless the user explicitly approves.

The schema contains:

- USERS
- ASSETS
- PRICE_HISTORY
- PORTFOLIOS
- PORTFOLIO_HOLDINGS
- TRADES
- RISK_INDICATORS
- AI_PREDICTIONS
- MARKET_SIGNALS
- HMM_STATES
- PORTFOLIO_OPTIMISATION
- ALERTS
- ALERT_LOGS
- SCRAPER_LOGS

Important:

- SENTIMENT_SCORES is removed in v2.
- RISK_INDICATORS replaces sentiment-based risk data.
- Do not add news tables, sentiment tables, AI summaries tables, or Claude chat tables.
- yfinance populates ASSETS, PRICE_HISTORY, and derived RISK_INDICATORS.
- Database triggers update holdings, cash, alert logs, and prediction actual_price backfill.

Before changing DB code:

1. Inspect existing schema files.
2. Compare against Database Schema v2.
3. Preserve PostgreSQL constraints.
4. Run SQL validation commands when possible.

# Architecture Overview

MarketMind is organized as a local-only monorepo with a clear split between frontend, backend, database, ETL, and future analytics work.

## Frontend

- The frontend lives in `frontend/`
- It uses React with JavaScript only
- Vite is the planned local development tool
- The frontend will later call backend APIs through a small service layer

## Backend

- The backend lives in `backend/`
- It uses FastAPI
- It will later expose APIs for assets, portfolios, trades, alerts, and authentication
- Authentication is planned as real JWT login, but not implemented during setup

## Database

- The database uses PostgreSQL
- The only schema definition is `database/marketmind_schema_v2_postgresql.sql`
- The project must follow Database Schema v2 exactly
- No Alembic or alternative migration system is part of the setup

## yfinance ETL

- ETL support is planned under the backend structure
- yfinance is intended only for asset metadata, OHLCV, beta, market cap, and risk-feature source data
- ETL remains local and schema-aligned

## AI Pipeline

- A future AI pipeline is planned as a lightweight backend module
- It should remain simple and demo-friendly
- It must write only to schema-approved structures such as existing prediction or signal tables
- It must not introduce news, sentiment, Claude, or AI summary/chat tables

## Scheduler and Jobs

- Background jobs are planned for local scheduling only
- Jobs can later support ETL refreshes, materialized view refreshes, and other approved local tasks
- The scheduler is part of the backend design, not a separate infrastructure service

## Database Triggers and Materialized Views

- Schema v2 includes 6 triggers
- Schema v2 includes 4 materialized views
- Trigger behavior handles holdings, cash, alert logs, and prediction actual-price backfill
- Materialized views provide read-friendly derived database outputs

## Current Scope

This repository currently documents and scaffolds the project only. It does not implement business features, authentication logic, ETL logic, AI logic, or production behavior yet.

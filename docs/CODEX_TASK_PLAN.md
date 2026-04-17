# Codex Task Plan

This file defines the planned build order for MarketMind after setup is complete. It is a future work plan only.

## Phase 1: DB verification

- Run the executable schema SQL file locally
- Verify Schema v2 counts and required objects
- Confirm the `marketmind` schema and search path behavior

## Phase 2: Backend skeleton

- Refine the existing FastAPI app entrypoint and package layout
- Keep the backend as structure only before feature work begins

## Phase 3: SQLAlchemy models

- Map SQLAlchemy models to the existing Schema v2 tables
- Keep model definitions aligned with the executable SQL schema

## Phase 4: JWT auth

- Add the real JWT login system planned by project decisions
- Keep auth aligned with existing schema constraints

## Phase 5: Asset APIs

- Add backend APIs for assets and approved read operations
- Keep endpoints aligned with existing database tables and views

## Phase 6: yfinance ETL

- Add local ETL support using yfinance only for approved market data fields
- Avoid news, sentiment, or schema-expanding ingestion

## Phase 7: Risk indicators

- Add risk-indicator computation and persistence using schema-approved tables only
- Keep the implementation simple and demo-friendly

## Phase 8: AI outputs

- Add lightweight AI and analytics outputs using existing prediction and signal structures
- Avoid overengineered pipelines and avoid unapproved tables

## Phase 9: Portfolio/trade/alert APIs

- Add backend APIs for portfolios, trades, and alerts
- Respect trigger-owned database behavior for holdings, cash, alert logs, and actual-price backfill

## Phase 10: React frontend

- Build out the React JavaScript frontend from the existing scaffold
- Keep the frontend local-only and aligned with backend APIs

## Phase 11: Final demo checks

- Verify local backend, frontend, and database flow together
- Check setup scripts, docs, and demo readiness before presentation or review

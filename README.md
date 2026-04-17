# MarketMind

MarketMind is a local-only stock and crypto intelligence platform for learning, development, and demo use. This repository is a monorepo scaffold for a React frontend, a FastAPI backend, and a PostgreSQL database built around Database Schema v2.

## Tech Stack

- Frontend: React with JavaScript only and Vite
- Backend: FastAPI
- Database: PostgreSQL
- Data ingestion: yfinance for approved market data only
- Analytics later: pandas, numpy, scikit-learn, hmmlearn, pgmpy, DEAP
- Charts later: Recharts

## Project Rules

- Use Database Schema v2 only.
- Use only `database/marketmind_schema_v2_postgresql.sql` as the schema source.
- Do not add Alembic.
- Do not add Docker.
- Keep development local-only.
- Do not add `SENTIMENT_SCORES`.
- Do not add news tables, sentiment tables, Claude tables, or AI summary/chat tables.
- Authentication will be a real JWT login system later, but it is not implemented yet.
- AI work should stay simple and demo-friendly when it is added later.

## Repository Structure

- `backend/` FastAPI project scaffold and backend dependency setup
- `frontend/` React + Vite JavaScript project scaffold
- `database/` executable PostgreSQL schema, verification SQL, and safe seed SQL
- `docs/` project decisions, architecture notes, runbook, and build plan
- `scripts/` PowerShell helper scripts for local checks

## Local-Only Setup

This project is designed for local development only right now.

- Run PostgreSQL locally.
- Create and use a local `marketmind` database.
- Run the backend locally from `backend/`.
- Run the frontend locally from `frontend/`.
- Use the PowerShell helper scripts in `scripts/` for quick environment checks.

## Basic Development Order

1. Run the PostgreSQL schema from `database/marketmind_schema_v2_postgresql.sql`.
2. Verify Schema v2 objects with `database/verification_queries.sql`.
3. Optionally seed the demo asset universe from `database/seed_assets.sql`.
4. Set up backend dependencies and environment variables.
5. Set up frontend dependencies and environment variables.
6. Build the project in phases using `docs/CODEX_TASK_PLAN.md`.

## Database Folder

The `database/` folder contains:

- `marketmind_schema_v2_postgresql.sql`
- `verification_queries.sql`
- `seed_assets.sql`

The schema file is the only database definition to use for this project.

## Check Scripts

The `scripts/` folder contains local PowerShell helpers:

- `scripts/check_database.ps1`
- `scripts/check_backend.ps1`
- `scripts/check_frontend.ps1`

These scripts are for environment and setup checks only.

## Important Note

MarketMind must stay aligned with Schema v2. No news, sentiment, Claude, AI summary, or extra chat tables are allowed unless the project owner explicitly changes that decision later.

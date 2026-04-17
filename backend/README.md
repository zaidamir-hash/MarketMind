# Backend

This folder contains the FastAPI backend foundation for MarketMind.

## Current State

- FastAPI app foundation only
- Environment-based configuration
- PostgreSQL connection wiring
- Health endpoints only
- No business endpoints yet
- No auth implementation yet
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

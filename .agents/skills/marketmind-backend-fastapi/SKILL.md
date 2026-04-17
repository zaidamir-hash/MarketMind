---
name: marketmind-backend-fastapi
description: Use when building or modifying the MarketMind FastAPI backend, routers, services, Pydantic schemas, SQLAlchemy models, auth, or API endpoints.
---

Build backend using:

- FastAPI
- SQLAlchemy 2.0
- Pydantic
- PostgreSQL
- environment variables for configuration
- real JWT authentication

Constraints:

- local development only unless the user says otherwise
- follow Database Schema v2 strictly
- use only the executable PostgreSQL SQL schema file as the database definition
- do not introduce Alembic unless explicitly requested
- do not add SENTIMENT_SCORES, news tables, sentiment tables, AI summaries tables, or Claude chat tables

Expected backend structure:

- app/main.py
- app/core/config.py
- app/db/session.py
- app/db/models.py or app/models/
- app/schemas/
- app/routers/
- app/services/
- app/jobs/

Never hardcode database passwords.

Keep route handlers thin:

- router receives request
- service handles logic
- model handles database structure

Use async only if the project is consistently async. Otherwise use normal SQLAlchemy sessions.

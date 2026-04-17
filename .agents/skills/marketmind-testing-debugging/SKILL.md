---
name: marketmind-testing-debugging
description: Use when debugging MarketMind backend, database, ETL jobs, AI pipelines, React frontend, or integration errors.
---

Debug systematically:

1. Reproduce the error.
2. Identify exact failing command/file.
3. Inspect logs.
4. Make the smallest fix.
5. Run verification command.
6. Explain what changed.

For backend:

- run pytest if available
- run FastAPI server
- test endpoints

For database:

- check psql connection
- verify tables, triggers, materialized views
- test sample inserts

For frontend:

- run npm install
- run npm run dev
- check browser console if available

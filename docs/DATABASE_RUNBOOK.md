# Database Runbook

This runbook explains how to load and verify the MarketMind PostgreSQL schema locally on Windows using `psql`.

## Source of Truth

Use only:

- `database/marketmind_schema_v2_postgresql.sql`

Do not use Alembic or any alternative migration system for this project unless explicitly requested later.

## Prerequisites

- PostgreSQL installed locally
- `psql` available in PowerShell, or use the full `psql.exe` path
- permission to create the local `marketmind` database with your PostgreSQL user

## Connect to the Database

The schema file already contains logic to create `marketmind` if it does not exist and then connect to it. For a first-time run, connect through a database that already exists, such as `postgres`.

Example command:

```powershell
psql -U postgres -d postgres
```

If your PostgreSQL installation is not on `PATH`, use the full executable path.

Example:

```powershell
& "C:/Program Files/PostgreSQL/17/bin/psql.exe" -U postgres -d postgres
```

## Run the Schema File

From the repository root, run:

```powershell
psql -U postgres -d postgres -f "database/marketmind_schema_v2_postgresql.sql"
```

Forward-slash Windows path example:

```powershell
psql -U postgres -d postgres -f "C:/Users/alize/Desktop/Uni Stuff/AI+DB+SDA Project/database/marketmind_schema_v2_postgresql.sql"
```

After the schema script finishes, you can connect directly to `marketmind`:

```powershell
psql -U postgres -d marketmind
```

## Set the Search Path

After connecting with `psql`, set:

```sql
SET search_path TO marketmind, public;
```

This keeps table and view access aligned with Schema v2.

## Verify Schema v2 Object Counts

Schema v2 should produce:

- 14 base tables
- 4 materialized views
- 6 triggers

Run the verification SQL:

```powershell
psql -U postgres -d marketmind -f "database/verification_queries.sql"
```

Or connect first and run:

```sql
\i database/verification_queries.sql
```

## Connect and Inspect Manually

Typical local session after the schema has been created:

```powershell
psql -U postgres -d marketmind
```

Then inside `psql`:

```sql
SET search_path TO marketmind, public;
\dt marketmind.*
\dm marketmind.*
```

## Common Windows `psql` Path Issue

On Windows, `psql` may fail with a message like "`psql` is not recognized" if PostgreSQL's `bin` folder is not on your `PATH`.

Two simple fixes:

1. Use the full executable path.
2. Add PostgreSQL's `bin` folder to your user `PATH` later if you want shorter commands.

Example full-path command:

```powershell
& "C:/Program Files/PostgreSQL/17/bin/psql.exe" -U postgres -d marketmind -f "C:/Users/alize/Desktop/Uni Stuff/AI+DB+SDA Project/database/verification_queries.sql"
```

## Expected Verification Goal

After the schema is loaded and the verification SQL is run, confirm:

- the `marketmind` schema exists
- 14 base tables exist
- 4 materialized views exist
- 6 triggers exist
- the required tables listed in `database/verification_queries.sql` are present

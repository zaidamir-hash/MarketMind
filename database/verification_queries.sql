-- MarketMind Schema v2 verification queries
-- Run after executing database/marketmind_schema_v2_postgresql.sql

SET search_path TO marketmind, public;

-- 1. Count base tables in schema marketmind
SELECT COUNT(*) AS base_table_count
FROM information_schema.tables
WHERE table_schema = 'marketmind'
  AND table_type = 'BASE TABLE';

-- 2. Count materialized views in schema marketmind
SELECT COUNT(*) AS materialized_view_count
FROM pg_matviews
WHERE schemaname = 'marketmind';

-- 3. Count triggers in schema marketmind
SELECT COUNT(*) AS trigger_count
FROM information_schema.triggers
WHERE trigger_schema = 'marketmind';

-- 4. List all base table names
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'marketmind'
  AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- 5. List all materialized views
SELECT matviewname AS materialized_view_name
FROM pg_matviews
WHERE schemaname = 'marketmind'
ORDER BY matviewname;

-- 6. List indexes in schema marketmind
SELECT
    tablename AS table_name,
    indexname AS index_name,
    indexdef AS index_definition
FROM pg_indexes
WHERE schemaname = 'marketmind'
ORDER BY tablename, indexname;

-- 7. List triggers and the tables they belong to
SELECT
    event_object_table AS table_name,
    trigger_name,
    action_timing,
    string_agg(event_manipulation, ', ' ORDER BY event_manipulation) AS trigger_events
FROM information_schema.triggers
WHERE trigger_schema = 'marketmind'
GROUP BY event_object_table, trigger_name, action_timing
ORDER BY event_object_table, trigger_name;

-- 8. Verify required tables exist
WITH required_tables(table_name) AS (
    VALUES
        ('users'),
        ('assets'),
        ('price_history'),
        ('portfolios'),
        ('portfolio_holdings'),
        ('trades'),
        ('risk_indicators'),
        ('ai_predictions'),
        ('market_signals'),
        ('hmm_states'),
        ('portfolio_optimisation'),
        ('alerts'),
        ('alert_logs'),
        ('scraper_logs')
)
SELECT
    rt.table_name,
    EXISTS (
        SELECT 1
        FROM information_schema.tables ist
        WHERE ist.table_schema = 'marketmind'
          AND ist.table_type = 'BASE TABLE'
          AND ist.table_name = rt.table_name
    ) AS exists_in_schema
FROM required_tables rt
ORDER BY rt.table_name;

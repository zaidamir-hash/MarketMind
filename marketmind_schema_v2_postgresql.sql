-- =====================================================================
-- MarketMind - Stock & Crypto Intelligence Platform
-- PostgreSQL Database Schema v2
-- Creates: 14 tables, 4 materialized views, 6 triggers, recommended indexes
-- Target: PostgreSQL 15+
-- =====================================================================

\set ON_ERROR_STOP on

-- ---------------------------------------------------------------------
-- CHANGE USERNAME / DATABASE NAME HERE
-- ---------------------------------------------------------------------
-- Replace postgres with YOUR PostgreSQL role/user name if needed.
-- Example: \set app_owner 'zeeshan'
\set app_owner 'postgres'

-- You can also rename the database here if required.
\set db_name 'marketmind'

-- ---------------------------------------------------------------------
-- Create database if it does not already exist, then connect to it.
-- This syntax is intended for running through psql / SQL Shell.
-- ---------------------------------------------------------------------
SELECT format('CREATE DATABASE %I OWNER %I', :'db_name', :'app_owner')
WHERE NOT EXISTS (
    SELECT 1 FROM pg_database WHERE datname = :'db_name'
);
\gexec

\connect :db_name

-- Required for gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Recreate a clean project schema.
-- WARNING: rerunning this file drops the marketmind schema and all objects inside it.
DROP SCHEMA IF EXISTS marketmind CASCADE;
CREATE SCHEMA marketmind AUTHORIZATION :"app_owner";
SET search_path TO marketmind, public;
ALTER DATABASE :"db_name" SET search_path = marketmind, public;

-- =====================================================================
-- 1) TABLES
-- =====================================================================

-- ---------------------------------------------------------------------
-- 01. USERS
-- ---------------------------------------------------------------------
CREATE TABLE users (
    user_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username       VARCHAR(50)  NOT NULL UNIQUE,
    email          VARCHAR(150) NOT NULL UNIQUE,
    password_hash  VARCHAR(255) NOT NULL,
    full_name      VARCHAR(100),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active      BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT chk_users_username_not_blank CHECK (length(trim(username)) > 0),
    CONSTRAINT chk_users_email_not_blank CHECK (length(trim(email)) > 0)
);

-- ---------------------------------------------------------------------
-- 02. ASSETS
-- ---------------------------------------------------------------------
CREATE TABLE assets (
    asset_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol      VARCHAR(20)  NOT NULL UNIQUE,
    name        VARCHAR(150) NOT NULL,
    asset_type  VARCHAR(10)  NOT NULL,
    exchange    VARCHAR(50),
    currency    VARCHAR(10)  NOT NULL DEFAULT 'USD',
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    added_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_assets_type CHECK (asset_type IN ('STOCK', 'CRYPTO')),
    CONSTRAINT chk_assets_symbol_not_blank CHECK (length(trim(symbol)) > 0),
    CONSTRAINT chk_assets_name_not_blank CHECK (length(trim(name)) > 0)
);

-- ---------------------------------------------------------------------
-- 03. PRICE_HISTORY
-- ---------------------------------------------------------------------
CREATE TABLE price_history (
    price_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id     UUID NOT NULL REFERENCES assets(asset_id),
    open_price   NUMERIC(18,6) NOT NULL,
    close_price  NUMERIC(18,6) NOT NULL,
    high_price   NUMERIC(18,6) NOT NULL,
    low_price    NUMERIC(18,6) NOT NULL,
    volume       BIGINT NOT NULL,
    interval     VARCHAR(10) NOT NULL DEFAULT '5min',
    recorded_at  TIMESTAMPTZ NOT NULL,

    CONSTRAINT uq_price_asset_time_interval UNIQUE (asset_id, recorded_at, interval),
    CONSTRAINT chk_price_non_negative CHECK (
        open_price >= 0 AND close_price >= 0 AND high_price >= 0 AND low_price >= 0
    ),
    CONSTRAINT chk_price_high_low CHECK (high_price >= low_price),
    CONSTRAINT chk_price_volume_non_negative CHECK (volume >= 0),
    CONSTRAINT chk_price_interval CHECK (interval IN ('5min', '1h', '1d'))
);

-- ---------------------------------------------------------------------
-- 04. PORTFOLIOS
-- ---------------------------------------------------------------------
CREATE TABLE portfolios (
    portfolio_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          UUID NOT NULL REFERENCES users(user_id),
    name             VARCHAR(100) NOT NULL,
    initial_capital  NUMERIC(15,2) NOT NULL DEFAULT 10000.00,
    current_cash     NUMERIC(15,2) NOT NULL DEFAULT 10000.00,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_default       BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT chk_portfolios_name_not_blank CHECK (length(trim(name)) > 0),
    CONSTRAINT chk_portfolios_initial_capital_positive CHECK (initial_capital >= 0),
    CONSTRAINT chk_portfolios_current_cash_non_negative CHECK (current_cash >= 0)
);

-- ---------------------------------------------------------------------
-- 05. PORTFOLIO_HOLDINGS
-- ---------------------------------------------------------------------
CREATE TABLE portfolio_holdings (
    holding_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_id   UUID NOT NULL REFERENCES portfolios(portfolio_id),
    asset_id       UUID NOT NULL REFERENCES assets(asset_id),
    quantity       NUMERIC(18,8) NOT NULL DEFAULT 0,
    avg_buy_price  NUMERIC(18,6) NOT NULL,
    last_updated   TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_holdings_portfolio_asset UNIQUE (portfolio_id, asset_id),
    CONSTRAINT chk_holdings_quantity_non_negative CHECK (quantity >= 0),
    CONSTRAINT chk_holdings_avg_buy_price_non_negative CHECK (avg_buy_price >= 0)
);

-- ---------------------------------------------------------------------
-- 06. TRADES
-- ---------------------------------------------------------------------
CREATE TABLE trades (
    trade_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_id    UUID NOT NULL REFERENCES portfolios(portfolio_id),
    asset_id        UUID NOT NULL REFERENCES assets(asset_id),
    trade_type      VARCHAR(4) NOT NULL,
    quantity        NUMERIC(18,8) NOT NULL,
    executed_price  NUMERIC(18,6) NOT NULL,
    total_value     NUMERIC(18,2) GENERATED ALWAYS AS (ROUND(quantity * executed_price, 2)) STORED,
    traded_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_trades_type CHECK (trade_type IN ('BUY', 'SELL')),
    CONSTRAINT chk_trades_quantity_positive CHECK (quantity > 0),
    CONSTRAINT chk_trades_executed_price_non_negative CHECK (executed_price >= 0)
);

-- ---------------------------------------------------------------------
-- 07. RISK_INDICATORS
-- ---------------------------------------------------------------------
CREATE TABLE risk_indicators (
    risk_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id           UUID NOT NULL REFERENCES assets(asset_id),
    beta               NUMERIC(8,4),
    volatility_30d     NUMERIC(8,6) NOT NULL,
    rsi_14             NUMERIC(6,2),
    volume_ratio       NUMERIC(8,4) NOT NULL,
    price_vs_52w_high  NUMERIC(8,4) NOT NULL,
    price_vs_sma50     NUMERIC(8,4) NOT NULL,
    market_cap_cat     VARCHAR(10),
    volatility_label   VARCHAR(10) NOT NULL,
    momentum_label     VARCHAR(10) NOT NULL,
    volume_label       VARCHAR(10) NOT NULL,
    risk_score         NUMERIC(6,4),
    risk_label         VARCHAR(10),
    computed_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_risk_rsi CHECK (rsi_14 IS NULL OR rsi_14 BETWEEN 0 AND 100),
    CONSTRAINT chk_risk_market_cap_cat CHECK (market_cap_cat IS NULL OR market_cap_cat IN ('LARGE', 'MID', 'SMALL', 'MICRO')),
    CONSTRAINT chk_risk_volatility_label CHECK (volatility_label IN ('HIGH', 'MEDIUM', 'LOW')),
    CONSTRAINT chk_risk_momentum_label CHECK (momentum_label IN ('BULLISH', 'NEUTRAL', 'BEARISH')),
    CONSTRAINT chk_risk_volume_label CHECK (volume_label IN ('SURGE', 'NORMAL', 'LOW')),
    CONSTRAINT chk_risk_score CHECK (risk_score IS NULL OR risk_score BETWEEN 0 AND 1),
    CONSTRAINT chk_risk_label CHECK (risk_label IS NULL OR risk_label IN ('HIGH', 'MEDIUM', 'LOW')),
    CONSTRAINT chk_risk_volatility_non_negative CHECK (volatility_30d >= 0),
    CONSTRAINT chk_risk_volume_ratio_non_negative CHECK (volume_ratio >= 0),
    CONSTRAINT chk_risk_price_vs_52w_high_range CHECK (price_vs_52w_high >= 0)
);

-- ---------------------------------------------------------------------
-- 08. AI_PREDICTIONS
-- ---------------------------------------------------------------------
CREATE TABLE ai_predictions (
    prediction_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id        UUID NOT NULL REFERENCES assets(asset_id),
    model_type      VARCHAR(30) NOT NULL,
    predicted_price NUMERIC(18,6) NOT NULL,
    confidence      NUMERIC(5,4),
    predicted_for   TIMESTAMPTZ NOT NULL,
    actual_price    NUMERIC(18,6),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_predictions_model_type_not_blank CHECK (length(trim(model_type)) > 0),
    CONSTRAINT chk_predictions_predicted_price_non_negative CHECK (predicted_price >= 0),
    CONSTRAINT chk_predictions_actual_price_non_negative CHECK (actual_price IS NULL OR actual_price >= 0),
    CONSTRAINT chk_predictions_confidence CHECK (confidence IS NULL OR confidence BETWEEN 0 AND 1)
);

-- ---------------------------------------------------------------------
-- 09. MARKET_SIGNALS
-- ---------------------------------------------------------------------
CREATE TABLE market_signals (
    signal_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id       UUID NOT NULL REFERENCES assets(asset_id),
    signal_type    VARCHAR(10) NOT NULL,
    model_source   VARCHAR(30) NOT NULL,
    strength       NUMERIC(5,4) NOT NULL,
    regime         VARCHAR(10),
    generated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_signals_type CHECK (signal_type IN ('BUY', 'SELL', 'HOLD')),
    CONSTRAINT chk_signals_strength CHECK (strength BETWEEN 0 AND 1),
    CONSTRAINT chk_signals_model_source_not_blank CHECK (length(trim(model_source)) > 0),
    CONSTRAINT chk_signals_regime CHECK (regime IS NULL OR regime IN ('BULL', 'BEAR', 'SIDEWAYS'))
);

-- ---------------------------------------------------------------------
-- 10. HMM_STATES
-- ---------------------------------------------------------------------
CREATE TABLE hmm_states (
    hmm_state_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id     UUID NOT NULL REFERENCES assets(asset_id),
    state_label  VARCHAR(10) NOT NULL,
    state_index  SMALLINT NOT NULL,
    probability  NUMERIC(6,5) NOT NULL,
    detected_at  TIMESTAMPTZ NOT NULL,

    CONSTRAINT chk_hmm_state_label CHECK (state_label IN ('BULL', 'BEAR', 'SIDEWAYS')),
    CONSTRAINT chk_hmm_state_index CHECK (state_index IN (0, 1, 2)),
    CONSTRAINT chk_hmm_probability CHECK (probability BETWEEN 0 AND 1)
);

-- ---------------------------------------------------------------------
-- 11. PORTFOLIO_OPTIMISATION
-- ---------------------------------------------------------------------
CREATE TABLE portfolio_optimisation (
    opt_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_id     UUID NOT NULL REFERENCES portfolios(portfolio_id),
    weights          JSONB NOT NULL,
    sharpe_ratio     NUMERIC(8,4) NOT NULL,
    expected_return  NUMERIC(8,4),
    expected_risk    NUMERIC(8,4),
    generations_run  INTEGER NOT NULL,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_optimisation_weights_object CHECK (jsonb_typeof(weights) = 'object'),
    CONSTRAINT chk_optimisation_generations_positive CHECK (generations_run > 0),
    CONSTRAINT chk_optimisation_expected_risk_non_negative CHECK (expected_risk IS NULL OR expected_risk >= 0)
);

-- ---------------------------------------------------------------------
-- 12. ALERTS
-- ---------------------------------------------------------------------
CREATE TABLE alerts (
    alert_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(user_id),
    asset_id    UUID NOT NULL REFERENCES assets(asset_id),
    condition   VARCHAR(10) NOT NULL,
    threshold   NUMERIC(18,6) NOT NULL,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_alerts_condition CHECK (condition IN ('ABOVE', 'BELOW')),
    CONSTRAINT chk_alerts_threshold_non_negative CHECK (threshold >= 0)
);

-- ---------------------------------------------------------------------
-- 13. ALERT_LOGS
-- ---------------------------------------------------------------------
CREATE TABLE alert_logs (
    log_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_id         UUID NOT NULL REFERENCES alerts(alert_id),
    triggered_price  NUMERIC(18,6) NOT NULL,
    fired_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_alert_logs_triggered_price_non_negative CHECK (triggered_price >= 0)
);

-- ---------------------------------------------------------------------
-- 14. SCRAPER_LOGS
-- ---------------------------------------------------------------------
CREATE TABLE scraper_logs (
    log_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_name       VARCHAR(60) NOT NULL,
    status         VARCHAR(10) NOT NULL,
    rows_inserted  INTEGER,
    error_message  TEXT,
    started_at     TIMESTAMPTZ NOT NULL,
    finished_at    TIMESTAMPTZ,

    CONSTRAINT chk_scraper_status CHECK (status IN ('SUCCESS', 'FAIL')),
    CONSTRAINT chk_scraper_rows_inserted_non_negative CHECK (rows_inserted IS NULL OR rows_inserted >= 0),
    CONSTRAINT chk_scraper_job_name_not_blank CHECK (length(trim(job_name)) > 0),
    CONSTRAINT chk_scraper_finished_after_started CHECK (finished_at IS NULL OR finished_at >= started_at)
);

-- =====================================================================
-- 2) MATERIALIZED VIEWS
-- =====================================================================

-- ---------------------------------------------------------------------
-- MV-01. mv_latest_prices
-- ---------------------------------------------------------------------
CREATE MATERIALIZED VIEW mv_latest_prices AS
SELECT DISTINCT ON (ph.asset_id)
    ph.asset_id,
    a.symbol,
    a.name,
    a.asset_type,
    ph.close_price AS current_price,
    ph.open_price,
    ph.high_price,
    ph.low_price,
    ph.volume,
    ph.recorded_at
FROM price_history ph
JOIN assets a ON a.asset_id = ph.asset_id
WHERE a.is_active = TRUE
ORDER BY ph.asset_id, ph.recorded_at DESC;

CREATE UNIQUE INDEX ux_mv_latest_prices_asset_id ON mv_latest_prices (asset_id);

-- ---------------------------------------------------------------------
-- MV-02. mv_portfolio_performance
-- ---------------------------------------------------------------------
CREATE MATERIALIZED VIEW mv_portfolio_performance AS
SELECT
    p.portfolio_id,
    p.user_id,
    p.name AS portfolio_name,
    p.initial_capital,
    p.current_cash,
    SUM(h.quantity * lp.current_price) AS holdings_value,
    p.current_cash + SUM(h.quantity * lp.current_price) AS total_value,
    (p.current_cash + SUM(h.quantity * lp.current_price) - p.initial_capital) AS total_pnl,
    ROUND(((p.current_cash + SUM(h.quantity * lp.current_price) - p.initial_capital)
        / NULLIF(p.initial_capital, 0)) * 100, 2) AS return_pct
FROM portfolios p
JOIN portfolio_holdings h ON h.portfolio_id = p.portfolio_id
JOIN mv_latest_prices lp ON lp.asset_id = h.asset_id
WHERE h.quantity > 0
GROUP BY p.portfolio_id, p.user_id, p.name, p.initial_capital, p.current_cash;

CREATE UNIQUE INDEX ux_mv_portfolio_performance_portfolio_id ON mv_portfolio_performance (portfolio_id);

-- ---------------------------------------------------------------------
-- MV-03. mv_asset_risk_summary
-- ---------------------------------------------------------------------
CREATE MATERIALIZED VIEW mv_asset_risk_summary AS
SELECT DISTINCT ON (ri.asset_id)
    ri.asset_id,
    a.symbol,
    a.name,
    a.asset_type,
    lp.current_price,
    ri.volatility_label,
    ri.momentum_label,
    ri.volume_label,
    ri.risk_label,
    ri.risk_score,
    ri.beta,
    ri.rsi_14,
    hm.state_label AS market_regime,
    ri.computed_at
FROM risk_indicators ri
JOIN assets a ON a.asset_id = ri.asset_id
JOIN mv_latest_prices lp ON lp.asset_id = ri.asset_id
LEFT JOIN LATERAL (
    SELECT state_label
    FROM hmm_states
    WHERE asset_id = ri.asset_id
    ORDER BY detected_at DESC
    LIMIT 1
) hm ON TRUE
WHERE a.is_active = TRUE
ORDER BY ri.asset_id, ri.computed_at DESC;

CREATE UNIQUE INDEX ux_mv_asset_risk_summary_asset_id ON mv_asset_risk_summary (asset_id);

-- ---------------------------------------------------------------------
-- MV-04. mv_signal_leaderboard
-- ---------------------------------------------------------------------
CREATE MATERIALIZED VIEW mv_signal_leaderboard AS
SELECT DISTINCT ON (ms.asset_id)
    ms.asset_id,
    a.symbol,
    a.name,
    ms.signal_type,
    ms.strength,
    ms.model_source,
    ms.regime,
    ms.generated_at,
    lp.current_price,
    rs.risk_label
FROM market_signals ms
JOIN assets a ON a.asset_id = ms.asset_id
JOIN mv_latest_prices lp ON lp.asset_id = ms.asset_id
LEFT JOIN mv_asset_risk_summary rs ON rs.asset_id = ms.asset_id
ORDER BY ms.asset_id, ms.generated_at DESC;

CREATE UNIQUE INDEX ux_mv_signal_leaderboard_asset_id ON mv_signal_leaderboard (asset_id);

-- =====================================================================
-- 3) TRIGGER FUNCTIONS AND TRIGGERS
-- =====================================================================

-- ---------------------------------------------------------------------
-- TRG-01. Update portfolio holdings after trade insert
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_update_holdings_on_trade()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.trade_type = 'BUY' THEN
        INSERT INTO portfolio_holdings
            (portfolio_id, asset_id, quantity, avg_buy_price)
        VALUES
            (NEW.portfolio_id, NEW.asset_id, NEW.quantity, NEW.executed_price)
        ON CONFLICT (portfolio_id, asset_id) DO UPDATE SET
            avg_buy_price = (
                (portfolio_holdings.quantity * portfolio_holdings.avg_buy_price
                 + NEW.quantity * NEW.executed_price)
                / NULLIF(portfolio_holdings.quantity + NEW.quantity, 0)
            ),
            quantity = portfolio_holdings.quantity + NEW.quantity,
            last_updated = NOW();

    ELSIF NEW.trade_type = 'SELL' THEN
        UPDATE portfolio_holdings
        SET quantity = quantity - NEW.quantity,
            last_updated = NOW()
        WHERE portfolio_id = NEW.portfolio_id
          AND asset_id = NEW.asset_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_01_update_holdings_on_trade
AFTER INSERT ON trades
FOR EACH ROW
EXECUTE FUNCTION fn_update_holdings_on_trade();

-- ---------------------------------------------------------------------
-- TRG-02. Update portfolio cash after trade insert
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_update_cash_on_trade()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.trade_type = 'BUY' THEN
        UPDATE portfolios
        SET current_cash = current_cash - NEW.total_value
        WHERE portfolio_id = NEW.portfolio_id;

    ELSIF NEW.trade_type = 'SELL' THEN
        UPDATE portfolios
        SET current_cash = current_cash + NEW.total_value
        WHERE portfolio_id = NEW.portfolio_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_02_update_cash_on_trade
AFTER INSERT ON trades
FOR EACH ROW
EXECUTE FUNCTION fn_update_cash_on_trade();

-- ---------------------------------------------------------------------
-- TRG-03. Refresh portfolio performance materialized view after trade
-- Note: PostgreSQL does not allow REFRESH MATERIALIZED VIEW CONCURRENTLY
-- inside a trigger transaction, so this trigger uses normal REFRESH.
-- Scheduled jobs can still run CONCURRENTLY outside triggers.
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_refresh_portfolio_mv()
RETURNS TRIGGER AS $$
BEGIN
    REFRESH MATERIALIZED VIEW mv_portfolio_performance;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_03_refresh_mv_after_trade
AFTER INSERT ON trades
FOR EACH ROW
EXECUTE FUNCTION fn_refresh_portfolio_mv();

-- ---------------------------------------------------------------------
-- TRG-04. Fire alerts after price history insert
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_fire_alert_on_price()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO alert_logs (alert_id, triggered_price)
    SELECT a.alert_id, NEW.close_price
    FROM alerts a
    WHERE a.asset_id = NEW.asset_id
      AND a.is_active = TRUE
      AND (
            (a.condition = 'ABOVE' AND NEW.close_price >= a.threshold)
         OR (a.condition = 'BELOW' AND NEW.close_price <= a.threshold)
      );

    UPDATE alerts
    SET is_active = FALSE
    WHERE asset_id = NEW.asset_id
      AND is_active = TRUE
      AND (
            (condition = 'ABOVE' AND NEW.close_price >= threshold)
         OR (condition = 'BELOW' AND NEW.close_price <= threshold)
      );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_04_fire_alert_on_price_insert
AFTER INSERT ON price_history
FOR EACH ROW
EXECUTE FUNCTION fn_fire_alert_on_price();

-- ---------------------------------------------------------------------
-- TRG-05. Validate SELL quantity before trade insert
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_validate_sell_quantity()
RETURNS TRIGGER AS $$
DECLARE
    held NUMERIC;
BEGIN
    IF NEW.trade_type = 'SELL' THEN
        SELECT COALESCE(quantity, 0)
        INTO held
        FROM portfolio_holdings
        WHERE portfolio_id = NEW.portfolio_id
          AND asset_id = NEW.asset_id;

        held := COALESCE(held, 0);

        IF held < NEW.quantity THEN
            RAISE EXCEPTION
                'SELL quantity % exceeds held quantity % for asset %',
                NEW.quantity, held, NEW.asset_id;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_05_validate_sell_quantity
BEFORE INSERT ON trades
FOR EACH ROW
EXECUTE FUNCTION fn_validate_sell_quantity();

-- ---------------------------------------------------------------------
-- TRG-06. Back-fill actual price for matured predictions after price insert
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_set_prediction_actual()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE ai_predictions
    SET actual_price = NEW.close_price
    WHERE asset_id = NEW.asset_id
      AND actual_price IS NULL
      AND predicted_for BETWEEN NEW.recorded_at - INTERVAL '5 minutes'
                            AND NEW.recorded_at + INTERVAL '5 minutes';

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_06_set_prediction_actual
AFTER INSERT ON price_history
FOR EACH ROW
EXECUTE FUNCTION fn_set_prediction_actual();

-- =====================================================================
-- 4) RECOMMENDED INDEXES
-- =====================================================================

CREATE INDEX idx_price_asset_time
    ON price_history (asset_id, recorded_at DESC);

CREATE INDEX idx_risk_asset_time
    ON risk_indicators (asset_id, computed_at DESC);

CREATE INDEX idx_trades_portfolio
    ON trades (portfolio_id, traded_at DESC);

CREATE INDEX idx_signals_asset
    ON market_signals (asset_id, generated_at DESC);

CREATE INDEX idx_pred_asset_model
    ON ai_predictions (asset_id, model_type);

CREATE INDEX idx_hmm_asset_time
    ON hmm_states (asset_id, detected_at DESC);

CREATE INDEX idx_alerts_active
    ON alerts (is_active)
    WHERE is_active = TRUE;

CREATE INDEX idx_assets_symbol
    ON assets (symbol);

-- Additional helpful FK indexes for joins and deletes/lookups.
CREATE INDEX idx_portfolios_user_id ON portfolios (user_id);
CREATE INDEX idx_holdings_asset_id ON portfolio_holdings (asset_id);
CREATE INDEX idx_trades_asset_id ON trades (asset_id);
CREATE INDEX idx_alerts_user_id ON alerts (user_id);
CREATE INDEX idx_alerts_asset_id ON alerts (asset_id);
CREATE INDEX idx_alert_logs_alert_id ON alert_logs (alert_id);
CREATE INDEX idx_optimisation_portfolio_id ON portfolio_optimisation (portfolio_id);
CREATE INDEX idx_scraper_logs_job_time ON scraper_logs (job_name, started_at DESC);

-- =====================================================================
-- 5) OWNERSHIP / PRIVILEGES
-- =====================================================================

ALTER SCHEMA marketmind OWNER TO :"app_owner";
GRANT USAGE, CREATE ON SCHEMA marketmind TO :"app_owner";
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA marketmind TO :"app_owner";
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA marketmind TO :"app_owner";
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA marketmind TO :"app_owner";

-- =====================================================================
-- 6) FINAL VERIFICATION OUTPUT
-- =====================================================================

\echo '------------------------------------------------------------'
\echo 'MarketMind Schema v2 creation completed.'
\echo 'Verification counts:'
\echo '------------------------------------------------------------'

SELECT 'tables' AS object_type, COUNT(*) AS object_count
FROM information_schema.tables
WHERE table_schema = 'marketmind'
  AND table_type = 'BASE TABLE'
UNION ALL
SELECT 'materialized_views' AS object_type, COUNT(*) AS object_count
FROM pg_matviews
WHERE schemaname = 'marketmind'
UNION ALL
SELECT 'triggers' AS object_type, COUNT(*) AS object_count
FROM information_schema.triggers
WHERE trigger_schema = 'marketmind'
UNION ALL
SELECT 'indexes' AS object_type, COUNT(*) AS object_count
FROM pg_indexes
WHERE schemaname = 'marketmind'
ORDER BY object_type;

\echo 'Expected main counts: 14 tables, 4 materialized views, 6 triggers.'

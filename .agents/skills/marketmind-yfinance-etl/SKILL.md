---
name: marketmind-yfinance-etl
description: Use when building MarketMind yfinance scrapers, OHLCV ingestion, asset metadata ingestion, risk feature computation, scheduler jobs, and scraper logs.
---

Use yfinance for:

- ticker metadata
- OHLCV history
- beta
- market cap
- historical windows for RSI, volatility, SMA, 52-week high, volume ratio

Write to:

- ASSETS
- PRICE_HISTORY
- RISK_INDICATORS
- SCRAPER_LOGS

Do not use yfinance news unless the user explicitly expands the schema.

Rules:

- Convert timestamps to UTC.
- Skip empty candles.
- Log scraper success/failure in SCRAPER_LOGS.
- Avoid duplicate PRICE_HISTORY rows for the same asset_id, recorded_at, interval.
- Compute:
  - volatility_30d
  - rsi_14
  - volume_ratio
  - price_vs_52w_high
  - price_vs_sma50
  - volatility_label
  - momentum_label
  - volume_label

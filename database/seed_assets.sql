-- MarketMind demo asset seed
-- Safe to re-run because inserts ignore existing symbols.

SET search_path TO marketmind, public;

INSERT INTO assets (symbol, name, asset_type, exchange, currency)
VALUES
    ('AAPL', 'Apple Inc.', 'STOCK', 'NASDAQ', 'USD'),
    ('MSFT', 'Microsoft Corporation', 'STOCK', 'NASDAQ', 'USD'),
    ('GOOGL', 'Alphabet Inc. Class A', 'STOCK', 'NASDAQ', 'USD'),
    ('TSLA', 'Tesla, Inc.', 'STOCK', 'NASDAQ', 'USD'),
    ('NVDA', 'NVIDIA Corporation', 'STOCK', 'NASDAQ', 'USD'),
    ('BTC-USD', 'Bitcoin USD', 'CRYPTO', 'CRYPTO', 'USD'),
    ('ETH-USD', 'Ethereum USD', 'CRYPTO', 'CRYPTO', 'USD')
ON CONFLICT (symbol) DO NOTHING;

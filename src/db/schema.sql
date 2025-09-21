--This directory holds SQL schema files and scripts for migration
--stock and stock_prices tables

CREATE TABLE IF NOT EXISTS stock_prices(
    PRIMARY KEY (symbol, timestamp)
    symbol TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    open
    high
    low
    close
    volume 
)

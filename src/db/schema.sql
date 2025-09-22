--This directory holds SQL schema files and scripts for migration
--stock and stock_prices tables

CREATE TABLE IF NOT EXISTS stock_data(
    PRIMARY KEY (symbol, timestamp)
    symbol TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL, --Stores both the date and time and the time zone offset.
    open NUMERIC(10,2), --10 total digits and 2 digits after the decimal point .00
    high NUMERIC(10, 2),
    low NUMERIC(10, 2),
    close NUMERIC(10, 2),
    volume BIGINT --A large integer type 64-bit. Volume is a big stock number so needs big ints for storage.
)

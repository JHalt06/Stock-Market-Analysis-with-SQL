--This direcotry is where SQL queires and analysis scripts
--Read from the database, not write to it.
--Add a query that shows something cool, like top gainers in last 24 hours, 52 week highs, etc.

SELECT MAX(timestamp) FROM day_prices WHERE ticker = ?
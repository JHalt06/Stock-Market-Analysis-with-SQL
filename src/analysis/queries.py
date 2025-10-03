from src.utils.db_utils import exec_get_all

rows = exec_get_all("""
    SELECT symbol, AVG(volume)
    FROM stock_data
    WHERE timestamp >= NOW() - INTERVAL '7 days'
    GROUP BY symbol
""") #learned NOW() and INTERVAL
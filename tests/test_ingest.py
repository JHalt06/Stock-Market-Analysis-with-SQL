from utils.db_utils import exec_get_one


def test_newest_timestamp():
    row = exec_get_one("""
    SELECT MAX(timestamp) FROM stock_data WHERE symbol = %s
    """, ("ASTS",))
    assert row is not None
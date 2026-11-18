import psycopg
from psycopg.rows import dict_row


def test_db_seed():
    with psycopg.connect() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT COUNT(*) FROM bag_reports")
            count = cur.fetchall()
            print(count)
            assert count[0]["count"] == 5
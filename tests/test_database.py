import psycopg
from psycopg.rows import dict_row
from found_item_search.server import get_one, get_bags, create_bag


def test_db_seed():
    with psycopg.connect() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT COUNT(*) FROM bag_reports")
            count = cur.fetchall()
            print(count)
            assert count[0]["count"] == 5

def test_get_bag_by_id(test_client):
    response = test_client.get("/reports/R-1001")
    assert response.status_code == 200
    data = response.json()
    assert data["report_id"] == "R-1001"
    assert data["colour"] == "blue"
    assert data["bag_form"] == "backpack"
    assert data["shell"] == "soft"
    assert data["brand"] == "brand_a"
    assert data["weight_kg"] == 2.5

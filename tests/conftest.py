import os

import psycopg
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

load_dotenv()

os.environ["PGDATABASE"] = "bag_reports_test"

PGPASSWORD = os.getenv("PGPASSWORD")
PGUSER = os.getenv("PGUSER")
PGHOST = os.getenv("PGHOST")
PGPORT = os.getenv("PGPORT")
PGDATABASE = os.getenv("PGDATABASE")

db_test_values = [
    ("R-1001", "blue", "backpack", "soft", "brand_a", 2.5),
    ("R-1002", "red", "duffel", "hard", "brand_b", 3.0),
    ("R-1003", "green", "suitcase", "soft", "brand_c", 4.5),
    ("R-1004", "yellow", "backpack", "hard", "brand_d", 1.8),
    ("R-1005", "black", "duffel", "soft", "brand_e", 2.2),
]


def db_seed():
    with psycopg.connect() as conn, conn.cursor() as cur:
        if conn.info.dbname == "bag_reports_test":
            for value in db_test_values:
                cur.execute(
                    "INSERT INTO bag_reports (report_id, colour, bag_form, shell, brand, weight_kg) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    value,
                )


def db_cleanup():
    with psycopg.connect() as conn, conn.cursor() as cur:
        if conn.info.dbname == "bag_reports_test":
            cur.execute("TRUNCATE bag_reports")


@pytest.fixture(autouse=True)
def db_setup():
    print("Cleaning up test database...")
    db_cleanup()

    print("Setting up test database...")
    db_seed()


@pytest.fixture()
def test_client():
    from found_item_search.server import app

    client = TestClient(app)
    return client

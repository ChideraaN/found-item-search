import os
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row
from .models import Bag
import csv

load_dotenv()

PGPASSWORD=os.getenv("PGPASSWORD")
PGUSER=os.getenv("PGUSER")
PGHOST=os.getenv("PGHOST")
PGPORT=os.getenv("PGPORT")
PGDATABASE=os.getenv("PGDATABASE")

def read_csv():
    with open('reports.csv', 'r', encoding='utf=8') as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    bags = []
    fails = []
    for row in rows:
        try:
            bag = Bag(**row)
            bags.append(bag)
        except ValueError as e:
            fails.append(row)


def insert_bags(bags):
    with psycopg.connect(f"dbname={PGDATABASE} user={PGUSER} password={PGPASSWORD} host={PGHOST} port={PGPORT}") as conn:
        with conn.cursor() as cur:
    
            cur.executemany("INSERT INTO bag_reports (report_id, colour, bag_form, shell, brand, weight_kg) " \
            "VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT(report_id) DO NOTHING", 
            [(bag.report_id, bag.colour, bag.bag_form, bag.shell, bag.brand, bag.weight_kg) for bag in bags])

        conn.commit()

def get_bag_report(report_id: str):
    with psycopg.connect() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "SELECT report_id, colour, bag_form, shell, brand, weight_kg " \
                "FROM bag_reports WHERE report_id = %s", (report_id,))
            bag_report = cur.fetchone()

    return bag_report

def create_bag_report(bag: Bag):
    with psycopg.connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO bag_reports (report_id, colour, bag_form, shell, brand, weight_kg) " \
                "VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT(report_id) DO NOTHING",
                (bag.report_id, bag.colour, bag.bag_form, bag.shell, bag.brand, bag.weight_kg)
            )
            if cur.rowcount == 0:
                    return None
            return bag
        
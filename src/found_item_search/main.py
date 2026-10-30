import os
from dotenv import load_dotenv
import psycopg
from models import Bag
import csv

load_dotenv()
PGPASSWORD=os.getenv("PGPASSWORD")
PGUSER=os.getenv("PGUSER")
PGHOST=os.getenv("PGHOST")
PGPORT=os.getenv("PGPORT")
PGDATABASE=os.getenv("PGDATABASE")

with open('reports.csv', 'r', encoding='utf=8') as file:
    reader = csv.DictReader(file)
    rows = list(reader)
    print(rows)

with psycopg.connect(f"dbname={PGDATABASE} user={PGUSER} password={PGPASSWORD} host={PGHOST} port={PGPORT}") as conn:
    with conn.cursor() as cur:
        
        cur.execute(f"SELECT * FROM {PGDATABASE}")
        for record in cur:
            print(record)

    conn.commit()
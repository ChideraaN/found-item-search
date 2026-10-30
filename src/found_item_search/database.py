import os
from dotenv import load_dotenv
import psycopg

load_dotenv()
PGPASSWORD=os.getenv("PGPASSWORD")
PGUSER=os.getenv("PGUSER")
PGHOST=os.getenv("PGHOST")
PGPORT=os.getenv("PGPORT")
PGDATABASE=os.getenv("PGDATABASE")

with psycopg.connect(f"dbname={PGDATABASE} user={PGUSER} password={PGPASSWORD} host={PGHOST} port={PGPORT}") as conn:
    with conn.cursor() as cur:

        cur.execute(
            "INSERT INTO bag_reports VALUES (%s, %s, %s, %s, %s, %s)",
            ('R-1005', 'white', 'backpack', 'soft', 'Bape', 6)
        )

        cur.execute(f"SELECT * FROM {PGDATABASE}")
        for record in cur:
            print(record)

    conn.commit()
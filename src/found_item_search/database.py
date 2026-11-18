import os
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row
from .models import Bag
import csv

load_dotenv()

def get_bag_report(report_id: str):
    with psycopg.connect() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "SELECT report_id, colour, bag_form, shell, brand, weight_kg "
                "FROM bag_reports WHERE report_id = %s",
                (report_id,),
            )
            bag_report = cur.fetchone()

    return bag_report


def create_bag_report(bag: Bag):
    with psycopg.connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO bag_reports (report_id, colour, bag_form, shell, brand, weight_kg) "
                "VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT(report_id) DO NOTHING",
                (
                    bag.report_id,
                    bag.colour,
                    bag.bag_form,
                    bag.shell,
                    bag.brand,
                    bag.weight_kg,
                ),
            )

            if cur.rowcount == 0:
                return None
            return bag


def get_bag_report_by_property(filters: dict[str, str | float], limit, offset):
    allowed_columns = {"colour", "bag_form", "shell", "brand", "weight_kg"}

    # these are the cols im searching for a match for e.g "colour"
    search_conditions = []

    # these are the match values im searching for e.g "blue"
    search_values = []

    for field, value in filters.items():
        if field not in allowed_columns:
            raise ValueError("Not a valid col in database", {field})

        search_conditions.append(f"{field} = %s")
        search_values.append(value)

    if search_conditions:
        where_clause = " AND ".join(search_conditions)
    else:
        where_clause = "TRUE"

    with psycopg.connect() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                f"""
                SELECT report_id, colour, bag_form, shell, brand, weight_kg
                FROM bag_reports
                WHERE {where_clause}
                ORDER BY report_id
                LIMIT %s
                OFFSET %s
                """,
                (search_values + [limit, offset]),
            )
            bag_reports = cur.fetchall()

    return bag_reports

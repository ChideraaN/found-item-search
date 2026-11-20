# found-item-search

A small REST API for lost-bag reports. You can create a report, fetch one by ID, and search reports by colour, bag form, shell, brand or weight. Built with FastAPI, Pydantic and PostgreSQL.

## Features

- `POST /reports` creates a bag report (201), or returns 409 if the `report_id` already exists
- `GET /reports/{report_id}` fetches one report, or returns 404
- `GET /reports` lists reports, with optional filters and pagination
- Input is validated with Pydantic, and the database adds its own constraints as a second check
- Integration tests run against a separate test database
- CI runs lint, type checks and tests on every push

## Tech stack

Python 3.12, FastAPI, Pydantic v2, psycopg 3, PostgreSQL 18, uv, pytest, ruff, pyright, Docker Compose, GitHub Actions

## Run it with Docker

1. Create a `.env` file in the project root (it is git-ignored, never commit it):

   ```
   PGUSER=postgres
   PGPASSWORD=choose-a-password
   PGDATABASE=bag_reports
   PGHOST=localhost
   PGPORT=5433
   ```

2. Start everything:

   ```
   docker compose up --build
   ```

3. Open http://localhost:8000/docs to try the API.

On first start, Postgres creates two databases, `bag_reports` (the app) and `bag_reports_test` (the tests), and loads `schema.sql` into both. This only runs on a fresh volume. To reset, run `docker compose down -v` and start again.

Port note: Postgres listens on 5432 inside the container and is published on 5433 on your machine, so it does not clash with a local Postgres.

## API

| Method | Path | Description |
| --- | --- | --- |
| POST | `/reports` | Create a report. 201 on success, 409 if the ID exists, 422 if the body is invalid |
| GET | `/reports/{report_id}` | Fetch one report. 404 if not found |
| GET | `/reports` | List reports with optional filters |

Filters on `GET /reports`: `colour`, `bag_form`, `shell`, `brand`, `weight_kg`. Filters combine with AND. Use `limit` and `offset` for paging.

Example:

```
GET /reports?colour=blue&bag_form=backpack&limit=10
```

Notes:
- Invalid values for `bag_form` or `shell` return 422.
- Unknown query parameters are ignored, not rejected.

## Run the tests

The tests need Postgres running with the `bag_reports_test` database (Docker Compose sets this up).

```
uv sync
uv run pytest
```

The test setup refuses to run against any database other than `bag_reports_test`, then empties and re-seeds the table before each test.

Checks that CI also runs:

```
uv run ruff check .
uv run ruff format --check .
uv run pyright
```

## Project layout

```
src/found_item_search/
  server.py      FastAPI routes
  models.py      Pydantic models
  database.py    SQL queries
tests/
  conftest.py    test database setup and fixtures
  test_database.py
schema.sql       table definition, used by Docker, tests and CI
docker/init-db.sql
Dockerfile
docker-compose.yml
```

## Design notes

- Queries are parameterised. Filter column names come from a fixed allow-list, so user input never becomes SQL.
- The schema is a single file reused by Docker, the tests and CI, so they cannot drift apart.

## Performance

`EXPLAIN ANALYZE` Output

# Before Index
"Limit  (cost=0.42..25.66 rows=100 width=42) (actual time=0.071..0.166 rows=100.00 loops=1)"
"  Buffers: shared hit=11"
"  ->  Index Scan using bag_reports_pkey on bag_reports  (cost=0.42..4239.42 rows=16793 width=42) (actual time=0.069..0.157 rows=100.00 loops=1)"
"        Filter: (colour = 'blue'::text)"
"        Rows Removed by Filter: 500"
"        Index Searches: 1"
"        Buffers: shared hit=11"
"Planning:"
"  Buffers: shared hit=37"
"Planning Time: 0.280 ms"
"Execution Time: 0.183 ms"

# After Index
"Limit  (cost=0.42..26.64 rows=100 width=42) (actual time=0.063..0.103 rows=100.00 loops=1)"
"  Buffers: shared hit=6 read=3"
"  ->  Index Scan using idx_bag_reports_colour_id on bag_reports  (cost=0.42..4231.98 rows=16140 width=42) (actual time=0.062..0.090 rows=100.00 loops=1)"
"        Index Cond: (colour = 'blue'::text)"
"        Index Searches: 1"
"        Buffers: shared hit=6 read=3"
"Planning:"
"  Buffers: shared hit=37 read=1"
"Planning Time: 0.417 ms"
"Execution Time: 0.135 ms"
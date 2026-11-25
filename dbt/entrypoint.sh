#!/bin/bash
set -e

echo "==> Initialising DuckDB with raw data..."
python /dbt/init_db.py

echo "==> Installing dbt packages..."
dbt deps

echo "==> Running dbt seed..."
dbt seed

echo "==> Running dbt run..."
dbt run

echo "==> Generating dbt docs (manifest + catalog)..."
dbt docs generate

echo "==> dbt pipeline complete."

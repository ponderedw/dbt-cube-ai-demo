#!/bin/bash
set -e

mkdir -p /app/superset_home

echo "==> Initialising Superset database..."
superset db upgrade

echo "==> Creating admin user..."
superset fab create-admin \
    --username admin \
    --firstname Admin \
    --lastname User \
    --email admin@demo.com \
    --password admin || true

echo "==> Initialising roles and permissions..."
superset init

echo "==> Starting Superset web server..."
superset run -p 8088 --host 0.0.0.0

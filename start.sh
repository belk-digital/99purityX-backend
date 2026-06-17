#!/bin/bash
set -e

echo "Running database migrations..."
alembic upgrade head || echo "No migrations to run or alembic not configured"

echo "Seeding database..."
python seed.py || echo "Seed already applied"

echo "Starting server..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}

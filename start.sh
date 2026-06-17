#!/bin/bash

echo "Running database migrations..."
alembic upgrade head 2>&1 || echo "Migrations skipped or already applied"

echo "Seeding database..."
python seed.py 2>&1 || echo "Seed skipped or already applied"

echo "Starting server on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}

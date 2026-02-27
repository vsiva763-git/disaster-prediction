#!/bin/bash
set -e

# Default to port 5000 if PORT is not set
PORT=${PORT:-5000}

echo "Starting Tsunami Detection API on port $PORT..."

# Start gunicorn with the PORT variable
exec gunicorn app:app \
  --bind 0.0.0.0:$PORT \
  --workers 2 \
  --timeout 120 \
  --log-level info \
  --access-logfile - \
  --error-logfile -

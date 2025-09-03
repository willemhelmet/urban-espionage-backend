#!/usr/bin/env bash
# exit on error
set -o errexit

# This script now uses Daphne for both HTTP and WebSocket support
python manage.py collectstatic --no-input
python manage.py migrate

# Start Daphne ASGI server (handles both HTTP and WebSocket)
daphne -b 0.0.0.0 -p 8000 examplesite.asgi:application

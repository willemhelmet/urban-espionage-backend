#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "Starting Urban Espionage with Daphne ASGI server..."

# Run Django setup commands
echo "Running collectstatic..."
python manage.py collectstatic --no-input

echo "Running migrations..."
python manage.py migrate

# Check if Redis is available (optional but recommended for channels)
echo "Checking Redis connection..."
python -c "
import os
import redis
r = redis.Redis(host=os.environ.get('REDIS_HOST', '127.0.0.1'), port=6379)
try:
    r.ping()
    print('Redis connection successful - full WebSocket features enabled')
except redis.ConnectionError:
    print('WARNING: Redis not available - WebSocket features will be limited')
"

# Start Daphne to handle both HTTP and WebSocket connections
echo "Starting Daphne ASGI server on port 8000..."
echo "Server will handle both HTTP and WebSocket connections"
daphne -b 0.0.0.0 -p 8000 \
    --access-log - \
    --ping-interval 20 \
    --ping-timeout 60 \
    examplesite.asgi:application
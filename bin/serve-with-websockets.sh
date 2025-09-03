#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "Starting Urban Espionage with WebSocket support..."

# Run Django setup commands
echo "Running collectstatic..."
python manage.py collectstatic --no-input

echo "Running migrations..."
python manage.py migrate

# Check if Redis is available
echo "Checking Redis connection..."
python -c "
import os
import redis
r = redis.Redis(host=os.environ.get('REDIS_HOST', '127.0.0.1'), port=6379)
try:
    r.ping()
    print('Redis connection successful')
except redis.ConnectionError:
    print('WARNING: Redis not available - WebSocket features will be limited')
"

# Start Daphne for WebSocket connections in the background
echo "Starting Daphne WebSocket server on port 8001..."
daphne -b 0.0.0.0:8001 examplesite.asgi:application &
DAPHNE_PID=$!
echo "Daphne started with PID $DAPHNE_PID"

# Give Daphne a moment to start
sleep 2

# Start Gunicorn for HTTP requests
echo "Starting Gunicorn HTTP server on port 8000..."
gunicorn -b 0.0.0.0:8000 \
    --workers 2 \
    --access-logformat '%(h)s %(l)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" reqtime: %(M)s ms' \
    examplesite.wsgi:application &
GUNICORN_PID=$!
echo "Gunicorn started with PID $GUNICORN_PID"

# Function to handle shutdown
cleanup() {
    echo "Shutting down servers..."
    kill $DAPHNE_PID 2>/dev/null || true
    kill $GUNICORN_PID 2>/dev/null || true
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

echo "Urban Espionage servers running:"
echo "  - HTTP API: http://localhost:8000"
echo "  - WebSocket: ws://localhost:8001"
echo "Press Ctrl+C to stop all servers"

# Wait for both processes
wait $DAPHNE_PID $GUNICORN_PID
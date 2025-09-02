#!/bin/bash

echo "Urban Espionage Backend Setup"
echo "=============================="
echo ""

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Please update .env with your configuration"
fi

# Build and start services
echo "Building Docker containers..."
docker-compose build

echo "Starting services..."
docker-compose up -d db redis

echo "Waiting for database to be ready..."
sleep 5

echo "Running database migrations..."
docker-compose run --rm web python manage.py makemigrations
docker-compose run --rm web python manage.py migrate

echo "Creating superuser (optional)..."
echo "Run: docker-compose run --rm web python manage.py createsuperuser"

echo ""
echo "Setup complete!"
echo ""
echo "To start the development server:"
echo "  docker-compose up"
echo ""
echo "The API will be available at:"
echo "  http://localhost:8000/api/"
echo ""
echo "WebSocket endpoint:"
echo "  ws://localhost:8001/ws/game/<game_code>/"
echo ""
echo "To stop services:"
echo "  docker-compose down"
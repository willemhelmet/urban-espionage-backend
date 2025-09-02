# Urban Espionage Backend

A real-time multiplayer AR game backend built with Django, PostgreSQL, Redis, and WebSockets. Players compete in teams (blue vs red) to complete espionage missions in the real world.

## 🎮 Game Overview

Urban Espionage is an augmented reality game where:
- Blue team (agents) complete tasks and defend objectives
- Red team (spies) sabotage and eliminate blue team members
- Players use real GPS locations to interact with the game world
- Items can be collected and used strategically
- Real-time updates via WebSocket connections

## 🚀 Quick Start with Docker

```bash
# Clone the repository
git clone <your-repo-url>
cd urban-espionage-backend

# Start all services
docker-compose up

# Backend is now running at:
# - REST API: http://localhost:8000/api/
# - WebSocket: ws://localhost:8001/ws/game/{game_code}/
# - Admin Panel: http://localhost:8000/admin/
```

## 📦 Services Architecture

| Service | Port | Purpose |
|---------|------|---------|
| **Django REST API** | 8000 | Game logic, player management, API endpoints |
| **Daphne WebSocket** | 8001 | Real-time position updates, chat, events |
| **PostgreSQL** | 5432 | Primary database for game data |
| **Redis** | 6379 | Cache and WebSocket message broker |

## 🧪 Testing the Backend

### Quick Test
```bash
# Run the quick test script
python3 quick_test.py

# Create a test game with sample data
docker-compose exec web python manage.py create_test_game --players 8 --start
```

### Interactive Testing
```bash
# Install test dependencies
pip install requests websocket-client

# Run interactive tester
python3 test_api.py
```

## 📡 API Endpoints

### Game Management
- `POST /api/games/` - Create new game
- `GET /api/games/{code}/` - Get game details
- `POST /api/games/{code}/join/` - Join game
- `POST /api/games/{code}/start/` - Start game
- `POST /api/games/{code}/leave/` - Leave game

### Player Actions
- `POST /api/players/{id}/update_position/` - Update GPS position
- `POST /api/players/{id}/pickup_item/` - Pick up item
- `POST /api/players/{id}/use_item/` - Use item from inventory

### Game Data
- `GET /api/events/?game_code={code}` - Get game events
- `GET /api/zones/?game_code={code}` - Get zones
- `GET /api/items/?game_code={code}` - Get items
- `GET /api/tasks/?game_code={code}` - Get tasks

## 🔌 WebSocket Events

Connect to `ws://localhost:8001/ws/game/{game_code}/`

### Outgoing Messages
```javascript
// Authenticate
{ type: 'authenticate', player_id: 'uuid' }

// Update position
{ type: 'position_update', lat: 37.7749, lng: -122.4194 }

// Request radar ping
{ type: 'radar_ping' }

// Send chat
{ type: 'chat', message: 'Hello team!', visibility: 'team' }
```

### Incoming Events
- `player_joined` - New player joined
- `player_moved` - Player position updated
- `item_collected` - Item picked up
- `task_launched` - New task started
- `player_killed` - Player eliminated
- `game_ended` - Game finished

## 🗂️ Database Models

| Model | Description |
|-------|-------------|
| **Game** | Game session with configuration and state |
| **Player** | Player profile, team, position, and status |
| **Zone** | Map areas (home base, tasks, revivers) |
| **ItemSpawn** | Collectible items on the map |
| **PlayerInventory** | Single-slot inventory system |
| **Task** | Mission objectives for teams |
| **Event** | Game activity log |

## 🛠️ Development

### Local Setup (without Docker)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### Management Commands

```bash
# Create test game
docker-compose exec web python manage.py create_test_game --players 10 --start

# Access Django shell
docker-compose exec web python manage.py shell

# View logs
docker-compose logs -f

# Reset database
docker-compose down -v
docker-compose up
```

## 📝 Example API Usage

### Create a Game
```bash
curl -X POST http://localhost:8000/api/games/ \
  -H "Content-Type: application/json" \
  -d '{
    "host_name": "GameMaster",
    "home_base_lat": 37.7749,
    "home_base_lng": -122.4194,
    "map_radius": 1000
  }'
```

### Join a Game
```bash
curl -X POST http://localhost:8000/api/games/ABC123/join/ \
  -H "Content-Type: application/json" \
  -d '{
    "player_name": "Agent007"
  }'
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find and kill process using port 8000
lsof -i :8000
kill <PID>
```

### Database Issues
```bash
# Reset database completely
docker-compose down -v
docker-compose up

# Re-run migrations
docker-compose exec web python manage.py migrate
```

### View Container Logs
```bash
docker-compose logs -f web      # Django logs
docker-compose logs -f daphne   # WebSocket logs
docker-compose logs -f db       # Database logs
```

## 📚 Documentation

- [Game Specification](../SPEC.md) - Complete game design document
- [Development Phases](../PHASES.md) - Implementation roadmap
- [Test Results](TEST_RESULTS.md) - Latest test outcomes
- [Postman Collection](urban_espionage.postman_collection.json) - API testing suite

## 🚢 Deployment

### Raspberry Pi Deployment
The backend is optimized for deployment on Raspberry Pi 4/5:

```bash
# Build for ARM architecture
docker buildx build --platform linux/arm64 -t urban-espionage-backend .

# Deploy with Docker Compose
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables
```env
DJANGO_SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost/dbname
REDIS_HOST=localhost
ALLOWED_HOSTS=your-domain.com
DEBUG=False
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📄 License

[Your License Here]

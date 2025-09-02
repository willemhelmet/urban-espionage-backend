# Urban Espionage Backend Testing Guide

## 🚀 Quick Start Testing

### 1. Start the Backend Services

```bash
# Make sure Docker is running, then:
./setup.sh        # First time only
docker-compose up # Start all services
```

Wait for services to be ready (database, Redis, Django).

### 2. Quick Test with Sample Data

```bash
# In a new terminal, create a test game with sample data:
docker-compose run --rm web python manage.py create_test_game --players 8 --start

# This will output a game code like: ABC123
```

## 🧪 Testing Methods

### Method 1: Interactive Python Script

```bash
# Install dependencies
pip install requests websocket-client

# Run the interactive tester
python test_api.py
```

Features:
- Interactive menu system
- Creates games, joins players, starts games
- Tests WebSocket connections
- Colored terminal output
- Full test suite option

### Method 2: Django Unit Tests

```bash
# Run all tests
docker-compose run --rm web python manage.py test

# Run specific test classes
docker-compose run --rm web python manage.py test core.tests.GameModelTest
docker-compose run --rm web python manage.py test core.tests.GameAPITest
docker-compose run --rm web python manage.py test core.tests.PlayerAPITest

# Run with coverage
docker-compose run --rm web coverage run --source='.' manage.py test
docker-compose run --rm web coverage report
```

### Method 3: Postman Collection

1. Import `urban_espionage.postman_collection.json` into Postman
2. Run requests in order:
   - Create Game
   - Join Game (multiple times for more players)
   - Start Game
   - Update Position
   - Get Events

The collection includes:
- Pre-request scripts
- Test assertions
- Variable management
- WebSocket connection info

### Method 4: cURL Commands

```bash
# Create a game
curl -X POST http://localhost:8000/api/games/ \
  -H "Content-Type: application/json" \
  -d '{
    "host_name": "TestHost",
    "home_base_lat": 37.7749,
    "home_base_lng": -122.4194,
    "map_radius": 1000
  }'

# Join a game (replace ABC123 with actual code)
curl -X POST http://localhost:8000/api/games/ABC123/join/ \
  -H "Content-Type: application/json" \
  -d '{"player_name": "TestPlayer"}'

# Start game
curl -X POST http://localhost:8000/api/games/ABC123/start/

# Get game details
curl http://localhost:8000/api/games/ABC123/
```

### Method 5: WebSocket Testing

#### Using wscat (command line)
```bash
# Install wscat
npm install -g wscat

# Connect to WebSocket
wscat -c ws://localhost:8001/ws/game/ABC123/

# Send messages:
> {"type": "authenticate", "player_id": "your-player-id"}
> {"type": "position_update", "lat": 37.7750, "lng": -122.4195}
> {"type": "radar_ping"}
```

#### Using JavaScript (browser console)
```javascript
const ws = new WebSocket('ws://localhost:8001/ws/game/ABC123/');

ws.onopen = () => {
  console.log('Connected');
  ws.send(JSON.stringify({
    type: 'authenticate',
    player_id: 'your-player-id'
  }));
};

ws.onmessage = (event) => {
  console.log('Received:', JSON.parse(event.data));
};

// Send position update
ws.send(JSON.stringify({
  type: 'position_update',
  lat: 37.7750,
  lng: -122.4195
}));
```

## 📊 Testing Scenarios

### Scenario 1: Basic Game Flow
1. Create game
2. Add 4-8 players
3. Start game
4. Verify team assignments
5. Update player positions
6. Check event log

### Scenario 2: Item Interaction
1. Create and start game
2. Get available items
3. Move player near item
4. Pick up item
5. Use item
6. Verify effects

### Scenario 3: Real-time Updates
1. Create game with multiple players
2. Connect multiple WebSocket clients
3. Send position update from one client
4. Verify other clients receive update
5. Test chat messages

### Scenario 4: Error Handling
1. Try joining non-existent game
2. Try joining started game
3. Try picking up distant item
4. Try starting game with 1 player
5. Verify appropriate error messages

## 🔍 Monitoring & Debugging

### View Django Logs
```bash
docker-compose logs -f web
```

### View Database
```bash
# Connect to PostgreSQL
docker-compose exec db psql -U urban_user -d urban_espionage

# Useful queries:
\dt                          # List tables
SELECT * FROM core_game;     # View games
SELECT * FROM core_player;   # View players
SELECT * FROM core_event ORDER BY created_at DESC LIMIT 10; # Recent events
```

### View Redis Cache
```bash
# Connect to Redis
docker-compose exec redis redis-cli

# Commands:
KEYS *                    # List all keys
GET game:ABC123          # Get game state
PUBSUB CHANNELS         # List active channels
```

### Django Admin Interface
1. Create superuser:
   ```bash
   docker-compose run --rm web python manage.py createsuperuser
   ```
2. Access admin at: http://localhost:8000/admin/
3. View and modify all game data

## 🐛 Common Issues & Solutions

### Issue: Cannot connect to backend
```bash
# Check if services are running
docker-compose ps

# Restart services
docker-compose down
docker-compose up
```

### Issue: Database migrations needed
```bash
docker-compose run --rm web python manage.py makemigrations
docker-compose run --rm web python manage.py migrate
```

### Issue: WebSocket connection fails
- Check if Daphne is running: `docker-compose ps daphne`
- Verify correct WebSocket URL format
- Check CORS settings if connecting from browser

### Issue: Tests fail with database errors
```bash
# Reset test database
docker-compose down -v
docker-compose up -d db
docker-compose run --rm web python manage.py migrate
```

## 📈 Performance Testing

### Load Testing with Locust
```python
# locustfile.py
from locust import HttpUser, task, between

class GameUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def create_game(self):
        self.client.post("/api/games/", json={
            "host_name": "LoadTest",
            "home_base_lat": 37.7749,
            "home_base_lng": -122.4194
        })
    
    @task(3)
    def get_games(self):
        self.client.get("/api/games/")

# Run: locust -f locustfile.py --host=http://localhost:8000
```

### Stress Testing WebSockets
```javascript
// Create multiple WebSocket connections
for (let i = 0; i < 50; i++) {
  const ws = new WebSocket('ws://localhost:8001/ws/game/ABC123/');
  ws.onopen = () => console.log(`Client ${i} connected`);
}
```

## ✅ Testing Checklist

- [ ] Backend services start successfully
- [ ] Can create a new game
- [ ] Can join game with multiple players
- [ ] Game starts with team assignments
- [ ] Player positions update correctly
- [ ] Items can be picked up and used
- [ ] Events are logged properly
- [ ] WebSocket connections work
- [ ] Real-time updates broadcast correctly
- [ ] Error responses are appropriate
- [ ] Django admin interface accessible
- [ ] Unit tests pass
- [ ] API endpoints return expected data
- [ ] Database constraints enforced
- [ ] Redis caching works

## 📚 Additional Resources

- [Django Testing Documentation](https://docs.djangoproject.com/en/5.0/topics/testing/)
- [Django REST Framework Testing](https://www.django-rest-framework.org/api-guide/testing/)
- [Channels Testing](https://channels.readthedocs.io/en/stable/topics/testing.html)
- [Postman Documentation](https://learning.postman.com/docs/getting-started/introduction/)
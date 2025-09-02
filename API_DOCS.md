# Urban Espionage Backend API Documentation

## Overview

The Urban Espionage backend provides REST API endpoints and WebSocket connections for real-time multiplayer gameplay.

## Quick Start

### Development Setup

1. Install Docker and Docker Compose
2. Clone the repository
3. Run the setup script:
   ```bash
   ./setup.sh
   ```
4. Start the services:
   ```bash
   docker-compose up
   ```

### Production Deployment (Raspberry Pi)

1. Copy `.env.example` to `.env` and configure production settings
2. Run production compose:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

## API Endpoints

### Base URL
- Development: `http://localhost:8000/api/`
- Production: `http://your-server/api/`

### Authentication
Currently using AllowAny permissions for MVP. Production will add JWT authentication.

### Games

#### Create Game
```
POST /api/games/
```
Request body:
```json
{
  "host_name": "Player Name",
  "avatar_url": "https://example.com/avatar.png",
  "home_base_lat": 37.7749,
  "home_base_lng": -122.4194,
  "map_radius": 1000,
  "max_players": 20,
  "game_duration": 60,
  "red_team_ratio": 0.25,
  "tasks_to_win": 5,
  "failures_to_lose": 2
}
```

Response:
```json
{
  "id": "uuid",
  "code": "ABC123",
  "status": "lobby",
  "home_base": {"lat": 37.7749, "lng": -122.4194},
  "config": {...},
  "players": [...],
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Join Game
```
POST /api/games/{code}/join/
```
Request body:
```json
{
  "player_name": "Player Name",
  "avatar_url": "https://example.com/avatar.png"
}
```

#### Start Game (Host Only)
```
POST /api/games/{code}/start/
```

#### Leave Game
```
POST /api/games/{code}/leave/
```
Request body:
```json
{
  "player_id": "uuid"
}
```

#### Get Game Details
```
GET /api/games/{code}/
```

#### List Games
```
GET /api/games/
```

### Players

#### Update Position
```
POST /api/players/{player_id}/update_position/
```
Request body:
```json
{
  "lat": 37.7749,
  "lng": -122.4194,
  "accuracy": 10.0
}
```

#### Pick Up Item
```
POST /api/players/{player_id}/pickup_item/
```
Request body:
```json
{
  "item_id": "uuid"
}
```

#### Use Item
```
POST /api/players/{player_id}/use_item/
```
Request body:
```json
{
  "target_player_id": "uuid",
  "target_position_lat": 37.7749,
  "target_position_lng": -122.4194
}
```

### Events

#### Get Game Events
```
GET /api/events/?game_code=ABC123
```

### Zones

#### Get Game Zones
```
GET /api/zones/?game_code=ABC123
```

### Items

#### Get Available Items
```
GET /api/items/?game_code=ABC123
```

### Tasks

#### Get Game Tasks
```
GET /api/tasks/?game_code=ABC123
```

## WebSocket Connection

### Connection URL
```
ws://localhost:8001/ws/game/{game_code}/
```

### Message Types

#### Client to Server

##### Authenticate
```json
{
  "type": "authenticate",
  "player_id": "uuid"
}
```

##### Position Update
```json
{
  "type": "position_update",
  "lat": 37.7749,
  "lng": -122.4194,
  "accuracy": 10.0
}
```

##### Radar Ping
```json
{
  "type": "radar_ping"
}
```

##### Chat Message
```json
{
  "type": "chat",
  "message": "Hello team!",
  "visibility": "team"
}
```

#### Server to Client

##### Player Joined
```json
{
  "type": "player_joined",
  "player": {...}
}
```

##### Player Moved
```json
{
  "type": "player_moved",
  "player_id": "uuid",
  "position": {"lat": 37.7749, "lng": -122.4194}
}
```

##### Game Started
```json
{
  "type": "game_started",
  "teams": {...}
}
```

##### Task Launched
```json
{
  "type": "task_launched",
  "task": {...}
}
```

##### Item Collected
```json
{
  "type": "item_collected",
  "item_id": "uuid",
  "player_id": "uuid"
}
```

##### Player Killed
```json
{
  "type": "player_killed",
  "victim_id": "uuid",
  "killer_id": "uuid",
  "cause": "dagger"
}
```

##### Game Ended
```json
{
  "type": "game_ended",
  "winner": "blue",
  "stats": {...}
}
```

## Game Flow

1. **Create Game**: Host creates a game and receives a 6-character code
2. **Join Lobby**: Players join using the code
3. **Start Game**: Host starts when ready (min 2 players)
4. **Team Assignment**: Players randomly assigned to blue/red teams
5. **Gameplay**: Players move, collect items, complete tasks
6. **Win Conditions**: 
   - Blue team: Complete 5 tasks
   - Red team: Cause 2 task failures
7. **Game End**: Stats displayed, option to rematch

## Environment Variables

```bash
# Django
DJANGO_SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com

# Database
DATABASE_URL=postgres://user:pass@host:5432/dbname
DB_USER=urban_user
DB_PASSWORD=secure-password

# Redis
REDIS_HOST=redis

# CORS (for frontend)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

## Testing

### Run Tests
```bash
docker-compose run --rm web python manage.py test
```

### Test WebSocket Connection
```javascript
const ws = new WebSocket('ws://localhost:8001/ws/game/ABC123/');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'authenticate',
    player_id: 'your-player-id'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

## Deployment Notes

### Raspberry Pi Optimization
- Uses Alpine Linux images for smaller footprint
- Multi-stage Docker build reduces image size
- Configured for ARM architecture
- Redis memory limit set to 256MB
- Gunicorn workers limited to 2

### Security Considerations
- Change `DJANGO_SECRET_KEY` in production
- Use HTTPS with proper SSL certificates
- Configure firewall rules
- Set up proper CORS origins
- Implement rate limiting
- Add authentication/authorization

## Troubleshooting

### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker-compose ps db

# View database logs
docker-compose logs db
```

### WebSocket Connection Failed
- Check if Daphne is running: `docker-compose ps daphne`
- Verify CORS settings
- Check nginx configuration for WebSocket upgrade headers

### Migration Issues
```bash
# Reset database (WARNING: Deletes all data)
docker-compose down -v
docker-compose up -d db
docker-compose run --rm web python manage.py migrate
```
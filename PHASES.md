# Urban Espionage Development Phases

## Phase 1: Core Foundation (1-2 weeks)

**Goal:** See yourself move on a map

Start with just a map and your location:

- Basic React app with routes (Title � Game screen)
- Leaflet map showing your current position
- Mock "other players" as static dots
- Simple Zustand store for game state
- No backend yet - just local state

### Phase 1 Tasks

- [x] Set up React Router with basic routes
- [x] Install and configure Tailwind CSS
- [x] Add Leaflet map to game screen
- [x] Implement location tracking with GPS
- [x] Add mock players on map
  - [x] Create Player componennt
  - [x] Generate 5-8 mock players within ~500m radius
  - [x] Create PlayerMarker component with icon and name
  - [x] Show different visual states (active/recent/dark)
  - [x] Add click interaction to show player details
  - [x] Display item indicator for players with items
  - [x] Ensure visual distinction from own marker
- [x] Create basic Zustand store
- [x] Style the UI with Tailwind
  - [x] Style Title screen with game branding
  - [x] Style Game screen with minimal HUD overlay
  - [x] Style map controls (recenter, zoom)
  - [x] Add responsive design for different screen sizes

## Phase 2: Django Backend & Game Lobby (1-2 weeks)

**Goal:** Multiple people can join same lobby via Django REST API

Backend infrastructure and multiplayer basics:

- Django REST Framework API on Raspberry Pi
- PostgreSQL database for game state
- Docker deployment for easy setup
- Create/join games with 6-character codes
- Real-time lobby updates via WebSockets
- Player list and game management

### Phase 2 Backend Tasks

- [ ] Set up disco project with REST framework
  - [ ] Initialize Django disco project structure
  - [ ] Add Django REST Framework and CORS headers (?)
  - [ ] Configure PostgreSQL database connection
  - [ ] Set up project settings for production
- [ ] Create Game and Player models
  - [ ] Game model (code, host, status, home_base, settings)
  - [ ] Player model (name, game_id, team, position, status)
  - [ ] Event model for game activity log
  - [ ] Add model serializers
- [ ] Implement game management API
  - [ ] POST /api/games/ - Create game with code generation
  - [ ] POST /api/games/{code}/join/ - Join game with player name
  - [ ] GET /api/games/{code}/ - Get game details
  - [ ] GET /api/games/{code}/players/ - List players in game
  - [ ] POST /api/games/{code}/start/ - Start game (host only)
  - [ ] DELETE /api/games/{code}/leave/ - Leave game
- [ ] Add WebSocket support with Django Channels
  - [ ] Install and configure Django Channels
  - [ ] Set up Redis for channel layer
  - [ ] Create WebSocket consumer for game rooms
  - [ ] Implement player join/leave notifications
  - [ ] Add game state change broadcasts
- [ ] Docker configuration for Raspberry Pi
  - [ ] Create multi-stage Dockerfile for ARM architecture
  - [ ] Write docker-compose.yml with Django, PostgreSQL, Redis
  - [ ] Add environment variable configuration
  - [ ] Create deployment scripts
  - [ ] Set up volume mounts for data persistence

### Phase 2 Frontend Tasks

- [ ] Install backend communication libraries
  - [ ] Add axios for REST API calls
  - [ ] Add socket.io-client for WebSockets
  - [ ] Configure environment variables for API endpoint
- [ ] Create API service layer
  - [ ] Game service (create, join, get details)
  - [ ] Player service (list, update position)
  - [ ] WebSocket service for real-time updates
  - [ ] Error handling and retry logic
- [ ] Update lobby screen with backend integration
  - [ ] Connect "New Game" to create game API
  - [ ] Display generated game code
  - [ ] Implement join game by code
  - [ ] Show real-time player list
  - [ ] Add loading and error states
- [ ] Update Zustand store for backend data
  - [ ] Store game code and game ID
  - [ ] Cache current player info
  - [ ] Manage player list
  - [ ] Track connection status
- [ ] Add game start flow
  - [ ] Host sets home base location
  - [ ] "Start Game" button for host only
  - [ ] Navigate all players to game screen on start

## Phase 3: Real-time Updates (1 week)

**Goal:** See other players move in real-time

Make it live:

- Add Socket.io or Firebase Realtime
- Show other players' actual positions
- Basic "visibility" system (active/inactive)
- Simple event log

### Phase 3 Tasks

- [ ] Set up WebSocket connections
- [ ] Broadcast player positions
- [ ] Implement visibility states
- [ ] Create event log component
- [ ] Handle player disconnect/reconnect

## Phase 4: Items System (1-2 weeks)

**Goal:** Pick up and use one item type

Add ONE item type first:

- Spawn items on map
- Pickup when nearby
- Single inventory slot
- Use item (start with something simple like "invisibility cloak")

### Phase 4 Tasks

- [ ] Create item spawn system
- [ ] Implement proximity detection
- [ ] Add inventory slot to UI
- [ ] Create item use mechanics
- [ ] Add visual feedback for item effects

## Phase 5: Tasks (1 week)

**Goal:** Complete a simple collaborative task

Implement ONE task type:

- "Capture objective" - just hold finger on screen
- Task zones on map
- Progress tracking
- Success/fail states

### Phase 5 Tasks

- [ ] Create task zones on map
- [ ] Implement task launching from home base
- [ ] Add progress bar UI
- [ ] Handle multiple players on same task
- [ ] Create success/failure notifications

## Phase 6: Win Conditions (3-4 days)

**Goal:** Play a complete round

Make it a game:

- Team assignment (blue/red)
- Task counter
- Game end screen
- Basic stats

### Phase 6 Tasks

- [ ] Implement team assignment on game start
- [ ] Add team reveal modal
- [ ] Create win condition logic
- [ ] Build post-game screen
- [ ] Display game statistics

## Future Phases (Post-MVP)

### Phase 7: Full Items Arsenal

- Implement all item types from spec
- Item respawn system
- Death and dogtag mechanics

### Phase 8: Advanced Tasks

- Add all task types
- Task rotation system
- Difficulty scaling

### Phase 9: Polish & Features

- Animations and transitions
- Sound effects
- Push notifications
- Tutorial system
- Profile customization

### Phase 10: Production Ready

- Security and anti-cheat
- Performance optimization
- Analytics
- Monetization (if applicable)

## Current Status

- **Active Phase:** Phase 1 - Core Foundation
- **Completed:** Basic routing, Tailwind setup, Leaflet map, GPS location
- **Next Steps:** Add mock players, create Zustand store

# Urban Espionage Specification
The purpose of this document is to create the outline of the game "Urban Espionage" (UE).
## Game overview
UE is an ARG-style game where players turn their own neighborhood into a board game.
The players are split up into "blue team" and "red team". The goal of the blue team is to complete a number of missions, while the red team's goal is to blend in with the blue team and thwart their progress!
If the blue team fails 3 tasks, or if they do not complete enough tasks before the end of the game, the red team wins.
### The Map
The players use their phone's map to interact with their environment in new ways.
A "home base" is set as a central point that all players frequent; this can be an office, school, gym, library, etc. This area defines a "safe zone" where players cannot hurt each other.
Surrounding the home base are items that players can walk to and add to their inventory.
Also there are "task zones", where players can congregate to complete tasks.
Players need to be in the immediate vincinity of an item or a task zone to interact with it.
### Items
Below is a small brainstorm list of possible items and their abilities:
- EMP: Creates a zone that disables all item activation within radius for a period of time
- Camera: Can record the identity of a player if they turn on the app in the area set up by the camera
- Time bomb: Explosive that goes off at a specific time
- Land mine: Explosive that goes off if a player gets within a certain radius
- Dagger: Kill another player close-by
- Mask: Appear as another player on the map for a set period of time
- Armor: Saves you from death if you have this item in your inventory and your are in a explosion radius
- Invisibility Cloak: Prevents your visibility status from becoming 'active', keeping you harder to spot
- Poison: When applied to another player, they will automatically fail challenges
- Motion Sensor: Sends user notification if player passes through radius
- Decoy: Places fake player marker on the map
- Dogtag: Dropped when a player dies, can be picked up and brought to a reviver zone to resurrect the dead player
### Game loop
One player creates a lobby, and sends invite codes to the other players.
Invites will be shared via a custom URL generated for each game
The "host" is the person creating the game instance. They get to choose the "home base".
Once enough players have joined a lobby, the "host" starts the game.
Each player is shown the Team Reveal Modal indicating what team they are on.
The map is populated with items, task zones, and reviver zones.
From this point on, the players on the "blue team" need to self-organize and try to complete tasks.
The "red team" will be trying to blend into the "blue team" and try to thwart tasks.
Blue team wins by completing 5 tasks. Red team wins if 2 tasks fail.
Dead players drop their inventory and dogtag at their death location, and can be revived if their dogtag is brought to a reviver zone. 
### Tasks
Tasks are launched by players from inside the HQ/home base zone. When a new task is launched, all players receive a notification about the task objectives.

Below is a small brainstorm list of possible tasks:
- Capture intel (1 zone): Pick up a special item (Briefcase?) and bring it back to HQ.
- Defuse bomb (2 zones): one zone has a bomb, and another zone has the information of which wire to cut.
- Capture objective (1 zone): Go to the "task zone" and hold your finger on the screen for 10 minutes. More than one person can do this task, making it go much faster.
- Password chain (2+ zones): Go to multiple zones to collect password fragments, go to the final zone to input the password

Tasks can fail if:
- Players fail the minigame (e.g., three wrong wire cuts in defuse bomb)
- The task timer expires without completion
- Red team successfully sabotages the task
## Views
This section describes the various window views that will be a part of the experience
### Title Screen
The main entry point when opening the app
- **Hero Logo** - Urban Espionage branding
- **Quick Join** - Input field for invite code + join button
- **Create Game** - Opens game creation flow (host only)
- **Active Games** - List of current games (shows status: lobby/in-progress)
- **Profile Button** - Shows avatar thumbnail, opens profile settings
- **Settings Gear** - Opens app settings
### Profile & Settings
Accessed from title screen
- **Profile Tab**
  - Avatar selector (preset options or custom upload)
  - Display name editor
  - Stats history (games played, win rate, favorite item, etc)
- **Permissions Tab**
  - Location permission status + enable button
  - Notification permission status + enable button
  - Background location toggle
  - Battery optimization warning
- **Accessibility Tab**
  - Colorblind modes
  - Larger UI elements toggle
  - Vibration patterns intensity
  - Screen reader support
### Lobby Screen
Pre-game waiting room
- **Invite Code** - Large display with copy button
- **Share Invite** - Native share sheet integration
- **Player List** - Shows who's joined
- **Map Preview** - Shows home base location
- **Game Settings** - (Host only) Configure duration, team ratios, map radius, home base location
- **Start Game** - (Host only) Begins game when enough players joined
- **Leave Lobby** - Exit back to title
### Team Reveal Modal
Shown immediately when game starts
- **Dramatic Reveal Animation** - Build suspense before showing team
- **Team Assignment** - Large "BLUE TEAM" or "RED TEAM" text
- **Team Color Background** - Full screen blue or red overlay
- **Mission Briefing** 
  - Blue: "Complete 5 tasks to secure victory. Trust no one."
  - Red: "Sabotage 2 tasks to win. Blend in. Deceive."
- **Dismiss Button** - "Begin Mission" to close modal and enter game
- **Auto-dismiss Timer** - Closes after 10 seconds if not dismissed
### Game Screen (Main HUD)
The primary gameplay interface - minimal UI overlaying the map
- **Map View** (Full screen)
  - Native map (Apple Maps/Google Maps/OpenMaps)
  - Your position (avatar icon)
  - Other players (only shows visible ones)
  - Zones as translucent overlays
  - Items
- **Top Bar** (Minimal height)
  - Your avatar (small) - hold to reveal team color
  - Task progress bar (if in task zone)
  - Events button (badge shows unread count)
- **Bottom Bar**
  - Current item slot (large tap target)
  - Use/Drop buttons appear when holding item
  - Recenter map button
- **Context-Sensitive Elements**
  - Task prompt appears when entering task zone
  - Item pickup button appears when near item
  - Player list appears when near other players
### Task Interaction Modal
Overlays when entering a task zone
- **Task Title** - e.g., "Defuse the Bomb"
- **Task Description** - Brief explanation
- **Participants** - Shows other players working on task
- **Progress Bar** - Visual completion indicator
- **Task-Specific UI**
  - Password input field (password_chain)
  - Wire selection buttons (defuse_bomb)
  - Hold button timer (capture_objective)
  - Briefcase status (capture_intel)
- **Leave Zone** - Abandon task button
### Event Log Screen
Full screen view of game events
- **Filter Tabs** - All/Team/Combat/Tasks
- **Event List** - Chronological with timestamps
  - Icon for event type
  - Color coding (team events blue/red, neutral white)
  - Tap event for details/location
- **Search** - Find specific player events
- **Close** - Return to game
### Item Use Modal
Context-sensitive based on item type
- **Target Selection** (for targeted items like dagger, poison)
  - List of nearby players
  - Range indicator
- **Placement Mode** (for deployables like cameras, mines)
  - Drag to position on map
  - Radius preview circle
- **Timer Setting** (for time_bomb)
  - Countdown selector
- **Confirm/Cancel** buttons
### Death Screen Modal
Overlay when player dies
- **"You Died" Message**
- **Cause of Death** - What killed you
- **Revival Instructions** - "A teammate must retrieve your dogtag and bring it to a reviver zone"
- **Spectator Mode Notice** - "You can still view the map and help your team"
### Post-Game Screen
Results after game ends
- **Winner Announcement** - Blue/Red team victory
- **Team Reveal** - Shows all players' true allegiances
- **MVP Awards**
  - Mission Specialist (most tasks completed)
  - Assassin (most kills)
  - Collector (most items gathered)
  - Saboteur (most tasks failed - red team)
  - Explorer (most distance traveled)
- **Statistics Grid**
  - Personal stats vs team average
  - Heat map of player movement
- **Rematch Button** - Start new game with same players
- **Share Results** - Social media integration
- **Return to Title** - Exit to main menu
### Tutorial Screen
Accessible from title screen or shown on first launch
- **Interactive Walkthrough**
  - Swipeable cards explaining core concepts
  - Team dynamics (blue vs red objectives)
  - How to pick up and use items
  - Task zones and completion
  - Death and revival mechanics
- **Practice Mode**
  - Mock mini-game demos
  - Item usage simulator
  - Map navigation basics
- **Reference Guide**
  - Quick access item descriptions
  - Task type explanations
  - Strategy tips
- **Skip Tutorial** - For experienced players
## API
This section describes the functions for the game's API.
### Types/Interfaces
```typescript 
interface Player {
  id: string;
  name: string;
  avatarUrl?: string;
  team: 'blue' | 'red';
  isAlive: boolean;
  statusEffects: StatusEffect[];
  isOnline: boolean;
  position: Coordinates;
  lastSeen: Date; // When position was last updated
  visibility: 'active' | 'recent' | 'dark'; // active: <2min, recent: 2-5min, dark: >5min; invisibility cloak prevents 'active'
  currentItem: Item | null; // Single inventory slot
  deathTime?: Date;
  deathPosition?: Coordinates; // Where player died (for dogtag location)
}

interface Coordinates {
  latitude: number;
  longitude: number;
  accuracy?: number;
  timestamp: Date;
}

interface Zone {
  id: string;
  type: 'home_base' | 'task' | 'item_spawn' | 'reviver' | 'emp_field';
  position: Coordinates;
  radius: number; // in meters
  metadata?: ZoneMetadata;
}

interface ZoneMetadata {
  createdBy?: string; // for EMP fields
  expiresAt?: Date; // for temporary zones like EMP fields
}

type ItemType = 
  | 'emp' | 'camera' | 'time_bomb' | 'land_mine' 
  | 'dagger' | 'mask' | 'armor' | 'invisibility_cloak' 
  | 'poison' | 'motion_sensor' | 'decoy' | 'dogtag';

interface Item {
  id: string;
  type: ItemType;
  ownerId?: string;
  usedAt?: Date;
  metadata?: ItemMetadata;
}

interface ItemMetadata {
  targetPlayerId?: string; // for mask
  detonationTime?: Date; // for time_bomb
  triggerRadius?: number; // for land_mine, motion_sensor
  duration?: number; // for temporary effects
  dogtagOwnerId?: string; // for dogtag - whose dogtag this is
}

interface ItemSpawn {
  id: string;
  type: ItemType;
  position: Coordinates;
  pickupRadius: number; // in meters
  available: boolean;
  collectedBy?: string;
  collectedAt?: Date;
  droppedBy?: string; // for player-dropped items (including death drops)
}

interface DeployedItem {
  id: string;
  type: ItemType;
  position: Coordinates;
  deployedBy: string;
  deployedAt: Date;
  active: boolean;
  metadata?: ItemMetadata;
}

interface StatusEffect {
  type: 'poisoned' | 'masked';
  expiresAt: Date;
  sourcePlayerId?: string; // who applied the effect
}

interface Task {
  id: string;
  type: 'capture_intel' | 'defuse_bomb' | 'capture_objective' | 'password_chain';
  zoneIds: string[];
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  participatingPlayers: string[]; // players currently working on this task
  progress: number; // 0-100
  metadata?: TaskMetadata;
}

interface TaskMetadata {
  passwordFragments?: string[];
  bombCode?: string;
  briefcaseId?: string;
  timeLimit?: number;
}

interface Game {
  id: string;
  hostId: string;
  status: 'lobby' | 'active' | 'completed';
  homeBase: Zone;
  players: Player[];
  tasks: Task[];
  items: ItemSpawn[];
  deployedItems: DeployedItem[];
  config: GameConfig;
  startTime?: Date;
  endTime?: Date;
  winner?: 'blue' | 'red';
  stats?: GameStats;
}

interface GameConfig {
  maxPlayers: number;
  gameDuration: number; // in minutes
  mapRadius: number; // in meters from home base
  redTeamRatio: number; // e.g., 0.25 for 25% red team
  winConditions: {
    tasksToWin: number; // default 5
    failuresToLose: number; // default 2
  };
}

interface GameStats {
  tasksCompleted: number;
  tasksFailed: number;
  itemsCollected: Record<string, number>; // by player id
  itemsUsed: Record<string, number>;
  kills: Record<string, number>;
  deaths: Record<string, number>;
  distanceTraveled: Record<string, number>; // in meters
}

type EventType = 
  | 'player_joined' | 'player_left' | 'game_started' 
  | 'player_moved' | 'item_picked' | 'item_used' 
  | 'task_started' | 'task_progress' | 'task_completed' 
  | 'task_failed' | 'player_killed' | 'game_ended'
  | 'motion_detected' | 'explosion' | 'item_respawn';

interface Event {
  id: string;
  gameId: string;
  type: EventType;
  visibility: 'public' | 'private' | 'team'; // who can see this
  recipientIds?: string[]; // for private events
  message: string;
  timestamp: Date;
  position?: Coordinates;
}
```
### Front End
This section describes the API for the front end
#### Core Services

```typescript
// Authentication & Player Management
class AuthService {
  async signIn(provider: 'google' | 'apple' | 'anonymous'): Promise<Player>;
  async signOut(): Promise<void>;
  async getCurrentPlayer(): Promise<Player | null>;
  async updateProfile(name: string, avatarUrl?: string): Promise<Player>;
}

// Game Lobby Management
class LobbyService {
  async createLobby(homeBase: Coordinates, config: GameConfig): Promise<Lobby>;
  async joinLobby(inviteCode: string): Promise<Lobby>;
  async leaveLobby(lobbyId: string): Promise<void>;
  async startGame(lobbyId: string): Promise<Game>; // host only
  async getLobby(lobbyId: string): Promise<Lobby>;
  subscribeLobbyUpdates(lobbyId: string, callback: (lobby: Lobby) => void): () => void;
}

// Active Game Management
class GameService {
  async getGame(gameId: string): Promise<Game>;
  async getActiveGames(): Promise<Game[]>;
  
  // Real-time subscriptions
  subscribeGameUpdates(gameId: string, callback: (game: Game) => void): () => void;
  subscribeEvents(gameId: string, callback: (event: Event) => void): () => void;
  subscribeNearbyItems(gameId: string, position: Coordinates, callback: (items: ItemSpawn[]) => void): () => void;
  subscribeNearbyZones(gameId: string, position: Coordinates, callback: (zones: Zone[]) => void): () => void;
}

// Player Actions
class PlayerActionService {
  // Movement & Visibility
  async updatePosition(gameId: string, position: Coordinates): Promise<void>; // Only works when app is active
  async sendRadarPing(gameId: string): Promise<Player[]>; // Returns visible players
  async goOffline(gameId: string): Promise<void>; // When app closes
  async comeOnline(gameId: string): Promise<Event[]>; // Returns missed events
  
  // Items
  async pickupItem(gameId: string, itemId: string): Promise<Item>;
  async dropItem(gameId: string): Promise<void>;
  async useItem(gameId: string, targetPlayerId?: string, targetPosition?: Coordinates): Promise<void>;
  
  // Tasks
  async launchTask(gameId: string, taskType: string): Promise<Task>; // Launch from home base zone
  async joinTask(gameId: string, taskId: string): Promise<void>;
  async leaveTask(gameId: string, taskId: string): Promise<void>;
  async submitTaskSolution(gameId: string, taskId: string, solution: any): Promise<void>;
}

// Map & Location Services
class MapService {
  async requestLocationPermission(): Promise<'granted' | 'denied' | 'prompt'>;
  async getCurrentPosition(): Promise<Coordinates>;
  watchPosition(callback: (position: Coordinates) => void, options?: { highAccuracy?: boolean }): () => void; // Active only when app is open
  
  async checkProximity(position1: Coordinates, position2: Coordinates): Promise<number>; // distance in meters
  async isInZone(position: Coordinates, zone: Zone): Promise<boolean>;
  async getNearbyPlayers(gameId: string, position: Coordinates, radius: number): Promise<Player[]>;
  async getVisiblePlayers(gameId: string): Promise<Player[]>; // accounts for invisibility, masks, etc
}

// Notification Management
class NotificationService {
  requestPermission(): Promise<boolean>;
  subscribeToNotifications(callback: (notification: Event) => void): () => void;
  async sendLocalNotification(title: string, body: string): Promise<void>;
}
```
#### React Hooks 

```typescript
// Custom hooks for common patterns
function useGame(gameId: string): {
  game: Game | null;
  loading: boolean;
  error: Error | null;
};

function usePlayerPosition(): {
  position: Coordinates | null;
  error: GeolocationPositionError | null;
  watching: boolean;
  startWatching: () => void;
  stopWatching: () => void;
};

function useNearbyItems(gameId: string, radius?: number): {
  items: ItemSpawn[];
  loading: boolean;
};

function useNearbyZones(gameId: string): {
  zones: Zone[];
  currentZone: Zone | null;
};

function useGameEvents(gameId: string, filter?: EventType[]): {
  events: Event[];
  latestEvent: Event | null;
};

function useCountdown(targetTime: Date): {
  timeRemaining: number; // in seconds
  expired: boolean;
};
```

#### State Management (Redux/Zustand style)

```typescript
interface GameState {
  // Current game
  currentGame: Game | null;
  currentPlayer: Player | null;
  
  // UI State
  mapCenter: Coordinates;
  selectedPlayer: Player | null;
  selectedZone: Zone | null;
  
  // Inventory
  currentItem: Item | null;
  
  // Events feed
  events: Event[];
  unreadEvents: number;
  
  // Actions
  actions: {
    joinGame: (inviteCode: string) => Promise<void>;
    updatePosition: (position: Coordinates) => void;
    pickupItem: (itemId: string) => Promise<void>;
    useItem: (targetId?: string) => Promise<void>;
    dropItem: () => Promise<void>;
  };
}
```
### Back End
This section describes the API for the back end

#### Architecture Overview

The backend uses a three-tier architecture optimized for real-time multiplayer gameplay:

```
[Mobile Apps] <-WebSocket-> [Node.js API Server] <-> [Redis Cache]
                                                  \-> [PostgreSQL + PostGIS]
```

**Technology Stack:**
- **Node.js + Express**: API server (TypeScript)
- **Socket.io**: WebSocket connections for real-time updates
- **PostgreSQL + PostGIS**: Persistent storage with spatial queries
- **Redis**: High-speed cache and pub/sub messaging
- **JWT**: Stateless authentication tokens

#### Data Flow Patterns

**High-frequency updates (player positions):**
1. Client sends position update via WebSocket
2. Server writes to Redis immediately
3. Redis pub/sub broadcasts to nearby players
4. Server batches PostgreSQL writes every 5-10 seconds

**Game state changes (item pickup, task completion):**
1. Client sends action request
2. Server validates against Redis cache
3. Atomically updates PostgreSQL (source of truth)
4. Updates Redis cache
5. Broadcasts event to relevant players

**Location-based queries:**
1. PostGIS handles "find within radius" queries efficiently
2. Results cached in Redis with short TTL (5-30 seconds)
3. Subsequent requests hit cache first

#### Database Schema (PostgreSQL)

```sql
-- Core tables with spatial support
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Players table
CREATE TABLE players (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email VARCHAR(255) UNIQUE,
  name VARCHAR(100) NOT NULL,
  avatar_url TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  last_seen TIMESTAMP,
  stats JSONB DEFAULT '{}'::jsonb
);

-- Games table
CREATE TABLE games (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  host_id UUID REFERENCES players(id),
  status VARCHAR(20) DEFAULT 'lobby', -- lobby, active, completed
  config JSONB NOT NULL,
  home_base GEOGRAPHY(POINT, 4326) NOT NULL,
  map_bounds GEOGRAPHY(POLYGON, 4326),
  started_at TIMESTAMP,
  ended_at TIMESTAMP,
  winner VARCHAR(10), -- blue, red
  created_at TIMESTAMP DEFAULT NOW()
);

-- Game players junction table
CREATE TABLE game_players (
  game_id UUID REFERENCES games(id) ON DELETE CASCADE,
  player_id UUID REFERENCES players(id),
  team VARCHAR(10) NOT NULL, -- blue, red
  is_alive BOOLEAN DEFAULT true,
  joined_at TIMESTAMP DEFAULT NOW(),
  left_at TIMESTAMP,
  PRIMARY KEY (game_id, player_id)
);

-- Zones (tasks, spawns, home base, reviver, emp fields)
CREATE TABLE zones (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  game_id UUID REFERENCES games(id) ON DELETE CASCADE,
  type VARCHAR(20) NOT NULL, -- home_base, task, item_spawn, reviver, emp_field
  position GEOGRAPHY(POINT, 4326) NOT NULL,
  radius_meters INTEGER NOT NULL,
  metadata JSONB DEFAULT '{}'::jsonb,
  active BOOLEAN DEFAULT true,
  expires_at TIMESTAMP -- for temporary zones like EMP fields
);

-- Player positions (tracks current location of active players)
CREATE TABLE player_positions (
  game_id UUID REFERENCES games(id) ON DELETE CASCADE,
  player_id UUID REFERENCES players(id),
  position GEOGRAPHY(POINT, 4326) NOT NULL,
  accuracy FLOAT,
  visibility VARCHAR(20) DEFAULT 'active', -- active, recent, dark
  updated_at TIMESTAMP DEFAULT NOW(),
  PRIMARY KEY (game_id, player_id)
);

-- Player inventories (single slot system)
CREATE TABLE player_inventories (
  game_id UUID REFERENCES games(id) ON DELETE CASCADE,
  player_id UUID REFERENCES players(id),
  item_id UUID REFERENCES item_spawns(id),
  item_type VARCHAR(30) NOT NULL,
  picked_up_at TIMESTAMP DEFAULT NOW(),
  PRIMARY KEY (game_id, player_id)
);

-- Deployed items (cameras, mines, sensors, etc.)
CREATE TABLE deployed_items (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  game_id UUID REFERENCES games(id) ON DELETE CASCADE,
  item_type VARCHAR(30) NOT NULL,
  position GEOGRAPHY(POINT, 4326) NOT NULL,
  deployed_by UUID REFERENCES players(id),
  deployed_at TIMESTAMP DEFAULT NOW(),
  active BOOLEAN DEFAULT true,
  metadata JSONB DEFAULT '{}'::jsonb,
  expires_at TIMESTAMP -- for temporary deployments
);

-- Items on the map (with respawning support)
CREATE TABLE item_spawns (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  game_id UUID REFERENCES games(id) ON DELETE CASCADE,
  item_type VARCHAR(30) NOT NULL,
  position GEOGRAPHY(POINT, 4326) NOT NULL,
  available BOOLEAN DEFAULT true,
  collected_by UUID REFERENCES players(id),
  collected_at TIMESTAMP,
  dropped_by UUID REFERENCES players(id), -- for death drops and manual drops
  respawn_at TIMESTAMP -- when this item should respawn
);

-- Tasks
CREATE TABLE tasks (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  game_id UUID REFERENCES games(id) ON DELETE CASCADE,
  type VARCHAR(30) NOT NULL,
  status VARCHAR(20) DEFAULT 'pending',
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP,
  failed_at TIMESTAMP
);

-- Game events log
CREATE TABLE events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  game_id UUID REFERENCES games(id) ON DELETE CASCADE,
  type VARCHAR(30) NOT NULL,
  player_id UUID REFERENCES players(id),
  position GEOGRAPHY(POINT, 4326),
  data JSONB DEFAULT '{}'::jsonb,
  visibility VARCHAR(20) DEFAULT 'public', -- public, team, private
  created_at TIMESTAMP DEFAULT NOW()
);

-- Spatial indexes for performance
CREATE INDEX idx_zones_position ON zones USING GIST(position);
CREATE INDEX idx_items_position ON item_spawns USING GIST(position);
CREATE INDEX idx_events_position ON events USING GIST(position);
CREATE INDEX idx_events_game_time ON events(game_id, created_at DESC);
CREATE INDEX idx_player_positions ON player_positions USING GIST(position);
CREATE INDEX idx_deployed_items_position ON deployed_items USING GIST(position);
CREATE INDEX idx_player_positions_visibility ON player_positions(game_id, visibility);
CREATE INDEX idx_items_respawn ON item_spawns(game_id, respawn_at) WHERE respawn_at IS NOT NULL;
```

#### Redis Data Structures

```typescript
// Redis key patterns and data structures

// Player positions (expires after 15 minutes - player goes fully dark)
// Key: position:{gameId}:{playerId}
{
  lat: number,
  lng: number,
  timestamp: number,
  accuracy: number,
  visibility: 'active' | 'recent' | 'dark'
}

// Active game state (expires 1 hour after game ends)
// Key: game:{gameId}
{
  status: string,
  players: Map<playerId, PlayerState>,
  activeTasks: Set<taskId>,
  deployedItems: Map<itemId, DeployedItem>
}

// Player inventory (expires with game)
// Key: inventory:{gameId}:{playerId}
{
  itemId: string,
  itemType: string,
  pickedUpAt: number
}

// Proximity cache (expires 5 seconds)
// Key: nearby:{gameId}:{lat}:{lng}:{radius}
{
  players: Array<PlayerId>,
  items: Array<ItemId>,
  zones: Array<ZoneId>
}

// Pub/Sub channels
// Channel: game:{gameId}:events - All game events
// Channel: game:{gameId}:positions - Position updates
// Channel: player:{playerId}:private - Private notifications
```

#### API Endpoints

```typescript
// REST endpoints for non-realtime operations
app.post('/api/auth/signin', authController.signIn);
app.post('/api/auth/signout', authController.signOut);

app.post('/api/games', authenticated, gameController.createGame);
app.get('/api/games/:id', authenticated, gameController.getGame);
app.post('/api/games/:id/join', authenticated, gameController.joinGame);
app.post('/api/games/:id/start', authenticated, isHost, gameController.startGame);

app.get('/api/players/:id/stats', playerController.getStats);
app.patch('/api/players/:id/profile', authenticated, playerController.updateProfile);

// WebSocket events
io.on('connection', (socket) => {
  // Join game room
  socket.on('join_game', async (gameId: string) => {
    await handleJoinGame(socket, gameId);
    socket.join(`game:${gameId}`);
  });

  // App lifecycle events
  socket.on('app_opened', async (data: AppOpened) => {
    // Player becomes visible, broadcast to nearby players
    await markPlayerActive(data.playerId);
    const nearbyPlayers = await getNearbyPlayers(data.position);
    socket.to(nearbyPlayers).emit('radar_ping', { playerId: data.playerId, position: data.position });
    
    // Send missed events
    const missedEvents = await getEventsSince(data.lastSeenTime);
    socket.emit('missed_events', missedEvents);
  });

  socket.on('app_closed', async (data: AppClosed) => {
    // Player immediately goes dark when app closes
    await markPlayerDark(data.playerId);
  });

  // Position updates (only while app is actively open)
  socket.on('update_position', async (data: PositionUpdate) => {
    // Only process if app is in foreground
    if (data.appState === 'active') {
      await updatePositionInRedis(data);
      await updatePlayerVisibility(data.playerId, 'active');
      socket.to(`game:${data.gameId}`).emit('player_moved', data);
    }
  });

  // Item interactions
  socket.on('pickup_item', async (data: ItemPickup) => {
    const result = await handleItemPickup(data);
    io.to(`game:${data.gameId}`).emit('item_collected', result);
  });

  // Task interactions
  socket.on('launch_task', async (data: TaskLaunch) => {
    const result = await handleTaskLaunch(data);
    io.to(`game:${data.gameId}`).emit('task_launched', result);
  });

  socket.on('join_task', async (data: TaskJoin) => {
    const result = await handleTaskJoin(data);
    io.to(`game:${data.gameId}`).emit('task_updated', result);
  });
});
```
#### Service Layer

```typescript
// Core service classes
class GameEngine {
  constructor(
    private redis: Redis,
    private db: PostgreSQL,
    private io: SocketIO.Server
  ) {}

  async processPlayerAction(action: PlayerAction): Promise<ActionResult> {
    // Validate action against game rules
    const gameState = await this.redis.get(`game:${action.gameId}`);
    const validation = this.validateAction(action, gameState);
    
    if (!validation.valid) {
      return { success: false, reason: validation.reason };
    }

    // Apply action
    const result = await this.applyAction(action, gameState);
    
    // Update caches
    await this.redis.set(`game:${action.gameId}`, result.newState);
    
    // Persist critical changes
    if (result.persistent) {
      await this.db.query(result.query);
    }
    
    // Broadcast events
    this.io.to(`game:${action.gameId}`).emit(result.event);
    
    return result;
  }
}

class ProximityService {
  constructor(private redis: Redis, private db: PostgreSQL) {}

  async findNearby(
    gameId: string, 
    position: Coordinates, 
    radius: number
  ): Promise<NearbyEntities> {
    // Check cache first
    const cacheKey = `nearby:${gameId}:${position.lat}:${position.lng}:${radius}`;
    const cached = await this.redis.get(cacheKey);
    if (cached) return cached;

    // Query PostGIS for spatial data
    const query = `
      SELECT id, type, ST_Distance(position, $1::geography) as distance
      FROM (
        SELECT id, 'player' as type, position FROM active_positions
        UNION ALL
        SELECT id, 'item' as type, position FROM item_spawns
        UNION ALL  
        SELECT id, 'zone' as type, position FROM zones
      ) as entities
      WHERE ST_DWithin(position, $1::geography, $2)
      ORDER BY distance;
    `;
    
    const result = await this.db.query(query, [position, radius]);
    
    // Cache with short TTL
    await this.redis.setex(cacheKey, 5, result);
    
    return result;
  }
}

class NotificationService {
  async sendGameEvent(gameId: string, event: GameEvent) {
    // Determine recipients based on visibility
    const recipients = await this.getEventRecipients(gameId, event);
    
    // Send via appropriate channels
    if (event.priority === 'high') {
      await this.sendPushNotification(recipients, event);
    }
    
    // Always send in-app
    await this.redis.publish(`game:${gameId}:events`, event);
  }
}
```
## Anti-Cheat & Security (AI slop)
To maintain fair gameplay, the following measures are proposed:

### GPS Spoofing Prevention
- **Velocity checks**: Flag players moving faster than humanly possible (>30mph between updates)
- **Location consistency**: Validate GPS accuracy values and reject suspicious jumps
- **Device fingerprinting**: Track device IDs to prevent multiple accounts per device
- **Cooldown on rejoins**: Players who disconnect can't rejoin for 30 seconds

### Game Integrity
- **Server-authoritative**: All game state changes validated server-side
- **Rate limiting**: API calls throttled per player (max 10 position updates/sec)
- **Action validation**: Check proximity and timing for all player actions
- **Encrypted communications**: Use TLS for all client-server communication

### Abuse Prevention
- **Report system**: Players can flag suspicious behavior for review
- **Replay system**: Store game events for post-game analysis
- **Trust scoring**: Track player behavior patterns across games
- **Temporary bans**: Automatic suspension for detected cheating

## Monetization
Every player can join a game for free, but you must buy/subscribe to create games. Maybe each account gets a limited number of games to create.
Purchasable items for accessorizing your avatar

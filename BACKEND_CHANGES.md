# Backend API Changes Required

## Problem
The Django backend API and React frontend have mismatched expectations for data formats, causing the admin panel and other features to fail.

## Current Issues

### 1. Case Convention Mismatch
- **Backend sends:** snake_case fields (`host_name`, `player_count`, `is_alive`)
- **Frontend expects:** camelCase fields (`hostName`, `playerCount`, `isAlive`)

### 2. Response Structure Differences

#### Game List Endpoint (`GET /api/games/`)
**Current Backend Response:**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [{
    "id": "...",
    "code": "2BECFF",
    "host_name": "TestHost",
    "player_count": 8,
    "max_players": 20
  }]
}
```

**Frontend Expects:**
```json
[{
  "id": "...",
  "code": "2BECFF",
  "hostId": "...",
  "players": [...],
  "maxPlayers": 20
}]
```

#### Game Detail Endpoint (`GET /api/games/{code}/`)
**Current Backend Response:**
```json
{
  "home_base": {
    "lat": 37.7749,
    "lng": -122.4194
  },
  "config": {
    "map_radius": 1000,
    "max_players": 20
  },
  "is_alive": true
}
```

**Frontend Expects:**
```json
{
  "homeBaseLat": 37.7749,
  "homeBaseLng": -122.4194,
  "mapRadius": 1000,
  "maxPlayers": 20,
  "isAlive": true
}
```

## Proposed Solution

### 1. Install djangorestframework-camel-case
```bash
pip install djangorestframework-camel-case
```

### 2. Update Django Settings
```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'djangorestframework_camel_case.render.CamelCaseJSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',  # Keep for debugging
    ),
    'DEFAULT_PARSER_CLASSES': (
        'djangorestframework_camel_case.parser.CamelCaseJSONParser',
        'rest_framework.parsers.JSONParser',
    ),
}
```

### 3. Update Serializers

#### GameListSerializer Changes
- Remove pagination from simple list endpoint OR
- Update frontend to handle paginated responses (recommended for scalability)
- Include full `players` array instead of just `player_count`
- Add `hostId` field

#### GameDetailSerializer Changes
- Flatten `home_base` object to `homeBaseLat` and `homeBaseLng`
- Flatten `config` object to top-level fields
- Ensure `hostId` is included

### 4. Field Mapping
Update all serializers to ensure these mappings:

| Current Backend | Should Be |
|-----------------|-----------|
| host_name | hostId (and return ID not name) |
| player_count | players (full array) |
| is_alive | isAlive |
| is_online | isOnline |
| avatar_url | avatarUrl |
| created_at | createdAt |
| started_at | startedAt |
| ended_at | endedAt |
| joined_at | joinedAt |
| home_base.lat | homeBaseLat |
| home_base.lng | homeBaseLng |
| config.map_radius | mapRadius |
| config.max_players | maxPlayers |
| config.game_duration | gameDuration |
| config.red_team_ratio | redTeamRatio |
| config.tasks_to_win | tasksToWin |
| config.failures_to_lose | failuresToLose |

## Benefits
1. **Single source of truth** - Frontend types match backend responses exactly
2. **No transformation layer needed** - Remove complex mapping functions
3. **Reduced bugs** - Eliminate field name mismatches
4. **Better maintainability** - Changes in one place affect both systems

## Implementation Priority
1.  Install and configure djangorestframework-camel-case
2.  Update GameDetailSerializer for game detail endpoint
3.  Update GameListSerializer for admin panel
4.  Update PlayerSerializer
5.  Test all endpoints with frontend

## Testing Checklist
- [ ] Admin panel shows games correctly
- [ ] Game creation works
- [ ] Game joining works
- [ ] Player list displays properly
- [ ] WebSocket events use camelCase
- [ ] Position updates work

## Alternative (Not Recommended)
If backend changes aren't possible, frontend would need:
- Transform layer for every API call
- Duplicate type definitions (API types vs domain types)
- Complex mapping functions
- Higher maintenance burden
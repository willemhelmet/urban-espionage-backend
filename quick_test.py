#!/usr/bin/env python3
import requests
import json

# Test API connection
print("Testing Urban Espionage Backend")
print("=" * 40)

# Get game details
game_code = "4LTFXS"
response = requests.get(f"http://localhost:8000/api/games/{game_code}/")

if response.status_code == 200:
    game = response.json()
    print(f"✓ Game found: {game['code']}")
    print(f"  Status: {game['status']}")
    print(f"  Players: {len(game['players'])}")
    
    # Show teams
    blue_team = [p for p in game['players'] if p.get('team') == 'blue']
    red_team = [p for p in game['players'] if p.get('team') == 'red']
    print(f"  Blue team: {len(blue_team)} players")
    print(f"  Red team: {len(red_team)} players")
    
    # Test position update for first player
    if game['players']:
        player = game['players'][0]
        player_id = player['id']
        print(f"\n✓ Testing position update for {player['name']}...")
        
        update_response = requests.post(
            f"http://localhost:8000/api/players/{player_id}/update_position/",
            json={"lat": 37.7750, "lng": -122.4195, "accuracy": 5.0}
        )
        
        if update_response.status_code == 200:
            print("  Position updated successfully!")
        else:
            print(f"  Failed: {update_response.status_code}")
    
    # Get events
    events_response = requests.get(f"http://localhost:8000/api/events/?game_code={game_code}")
    if events_response.status_code == 200:
        events = events_response.json()['results']
        print(f"\n✓ Events: {len(events)} total")
        for event in events[:3]:
            print(f"  - [{event['type']}] {event['message']}")
    
    print(f"\n✓ API is working!")
    print(f"\nYou can now:")
    print(f"1. Join more players: POST /api/games/{game_code}/join/")
    print(f"2. Connect WebSocket: ws://localhost:8001/ws/game/{game_code}/")
    print(f"3. View in browser: http://localhost:8000/api/games/{game_code}/")
    
else:
    print(f"✗ Failed to get game: {response.status_code}")
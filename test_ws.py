#!/usr/bin/env python3
import websocket
import json
import threading
import time

def on_message(ws, message):
    print(f"Received: {message}")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print(f"Closed: {close_status_code} - {close_msg}")

def on_open(ws):
    print("Connected! Sending authentication...")
    
    # Get a valid player ID from the game
    import requests
    response = requests.get("http://localhost:8000/api/games/4LTFXS/")
    game_data = response.json()
    
    if game_data and game_data.get('players'):
        player_id = game_data['players'][0]['id']
        auth_msg = json.dumps({
            'type': 'authenticate',
            'player_id': player_id
        })
        ws.send(auth_msg)
        print(f"Sent authentication for player: {player_id}")
        
        # Send a position update after auth
        time.sleep(1)
        pos_msg = json.dumps({
            'type': 'position_update',
            'lat': 37.7749,
            'lng': -122.4194
        })
        ws.send(pos_msg)
        print("Sent position update")

if __name__ == "__main__":
    ws = websocket.WebSocketApp("ws://localhost:8001/ws/game/4LTFXS/",
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    
    ws.run_forever()
#!/usr/bin/env python3
"""
Interactive API Testing Script for Urban Espionage Backend

This script allows you to test the API endpoints interactively.
Run with: python test_api.py
"""

import requests
import json
import time
import random
import websocket
import threading
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"
WS_URL = "ws://localhost:8001/ws"

# ANSI color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class UrbanEspionageAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.current_game = None
        self.current_player = None
        self.ws_connection = None
        
    def print_header(self, text: str):
        """Print a formatted header"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*50}")
        print(f"{text}")
        print(f"{'='*50}{Colors.RESET}\n")
    
    def print_success(self, text: str):
        """Print success message"""
        print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")
    
    def print_error(self, text: str):
        """Print error message"""
        print(f"{Colors.RED}✗ {text}{Colors.RESET}")
    
    def print_info(self, text: str):
        """Print info message"""
        print(f"{Colors.CYAN}ℹ {text}{Colors.RESET}")
    
    def print_json(self, data: Dict):
        """Pretty print JSON data"""
        print(f"{Colors.YELLOW}{json.dumps(data, indent=2)}{Colors.RESET}")
    
    def test_create_game(self) -> Optional[Dict]:
        """Test creating a new game"""
        self.print_header("Testing: Create Game")
        
        data = {
            "host_name": f"TestHost_{random.randint(1000, 9999)}",
            "home_base_lat": 37.7749,
            "home_base_lng": -122.4194,
            "map_radius": 1000,
            "max_players": 10,
            "game_duration": 30,
            "red_team_ratio": 0.3,
            "tasks_to_win": 5,
            "failures_to_lose": 2
        }
        
        try:
            response = self.session.post(f"{API_URL}/games/", json=data)
            response.raise_for_status()
            
            game_data = response.json()
            self.current_game = game_data
            
            self.print_success(f"Game created with code: {game_data['code']}")
            self.print_info(f"Game ID: {game_data['id']}")
            self.print_info(f"Status: {game_data['status']}")
            
            # Extract host player
            if game_data.get('players'):
                self.current_player = game_data['players'][0]
                self.print_info(f"Host player ID: {self.current_player['id']}")
            
            return game_data
            
        except requests.exceptions.RequestException as e:
            self.print_error(f"Failed to create game: {e}")
            return None
    
    def test_join_game(self, game_code: str = None) -> Optional[Dict]:
        """Test joining a game"""
        self.print_header("Testing: Join Game")
        
        if not game_code and self.current_game:
            game_code = self.current_game['code']
        
        if not game_code:
            self.print_error("No game code provided")
            return None
        
        data = {
            "player_name": f"Player_{random.randint(1000, 9999)}",
            "avatar_url": "https://example.com/avatar.png"
        }
        
        try:
            response = self.session.post(f"{API_URL}/games/{game_code}/join/", json=data)
            response.raise_for_status()
            
            player_data = response.json()
            
            self.print_success(f"Joined game {game_code}")
            self.print_info(f"Player name: {player_data['name']}")
            self.print_info(f"Player ID: {player_data['id']}")
            
            return player_data
            
        except requests.exceptions.RequestException as e:
            self.print_error(f"Failed to join game: {e}")
            if hasattr(e.response, 'json'):
                self.print_json(e.response.json())
            return None
    
    def test_start_game(self, game_code: str = None) -> bool:
        """Test starting a game"""
        self.print_header("Testing: Start Game")
        
        if not game_code and self.current_game:
            game_code = self.current_game['code']
        
        if not game_code:
            self.print_error("No game code provided")
            return False
        
        try:
            response = self.session.post(f"{API_URL}/games/{game_code}/start/")
            response.raise_for_status()
            
            game_data = response.json()
            self.current_game = game_data
            
            self.print_success(f"Game {game_code} started!")
            self.print_info(f"Status: {game_data['status']}")
            
            # Show team assignments
            if 'players' in game_data:
                blue_team = [p for p in game_data['players'] if p.get('team') == 'blue']
                red_team = [p for p in game_data['players'] if p.get('team') == 'red']
                
                self.print_info(f"Blue team: {len(blue_team)} players")
                self.print_info(f"Red team: {len(red_team)} players")
            
            return True
            
        except requests.exceptions.RequestException as e:
            self.print_error(f"Failed to start game: {e}")
            if hasattr(e.response, 'json'):
                self.print_json(e.response.json())
            return False
    
    def test_update_position(self, player_id: str = None) -> bool:
        """Test updating player position"""
        self.print_header("Testing: Update Position")
        
        if not player_id and self.current_player:
            player_id = self.current_player['id']
        
        if not player_id:
            self.print_error("No player ID provided")
            return False
        
        # Generate random position near home base
        lat = 37.7749 + random.uniform(-0.001, 0.001)
        lng = -122.4194 + random.uniform(-0.001, 0.001)
        
        data = {
            "lat": lat,
            "lng": lng,
            "accuracy": 5.0
        }
        
        try:
            response = self.session.post(
                f"{API_URL}/players/{player_id}/update_position/",
                json=data
            )
            response.raise_for_status()
            
            player_data = response.json()
            
            self.print_success(f"Position updated")
            self.print_info(f"New position: ({lat:.6f}, {lng:.6f})")
            self.print_info(f"Visibility: {player_data.get('visibility', 'unknown')}")
            
            return True
            
        except requests.exceptions.RequestException as e:
            self.print_error(f"Failed to update position: {e}")
            return False
    
    def test_get_events(self, game_code: str = None) -> Optional[list]:
        """Test getting game events"""
        self.print_header("Testing: Get Events")
        
        if not game_code and self.current_game:
            game_code = self.current_game['code']
        
        if not game_code:
            self.print_error("No game code provided")
            return None
        
        try:
            response = self.session.get(f"{API_URL}/events/?game_code={game_code}")
            response.raise_for_status()
            
            events_data = response.json()
            events = events_data.get('results', [])
            
            self.print_success(f"Retrieved {len(events)} events")
            
            # Show last 5 events
            for event in events[:5]:
                self.print_info(
                    f"[{event['type']}] {event['message']} "
                    f"(visibility: {event['visibility']})"
                )
            
            return events
            
        except requests.exceptions.RequestException as e:
            self.print_error(f"Failed to get events: {e}")
            return None
    
    def test_websocket_connection(self, game_code: str = None, player_id: str = None):
        """Test WebSocket connection"""
        self.print_header("Testing: WebSocket Connection")
        
        if not game_code and self.current_game:
            game_code = self.current_game['code']
        
        if not player_id and self.current_player:
            player_id = self.current_player['id']
        
        if not game_code:
            self.print_error("No game code provided")
            return
        
        ws_url = f"{WS_URL}/game/{game_code}/"
        
        def on_message(ws, message):
            data = json.loads(message)
            self.print_info(f"WS Received: {data.get('type', 'unknown')}")
            if data.get('type') == 'error':
                self.print_error(f"WS Error: {data.get('message')}")
        
        def on_error(ws, error):
            self.print_error(f"WebSocket error: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            self.print_info("WebSocket connection closed")
        
        def on_open(ws):
            self.print_success("WebSocket connected")
            
            # Send authentication if we have a player ID
            if player_id:
                auth_msg = json.dumps({
                    "type": "authenticate",
                    "player_id": player_id
                })
                ws.send(auth_msg)
                self.print_info(f"Sent authentication for player {player_id}")
            
            # Send a test position update
            time.sleep(1)
            pos_msg = json.dumps({
                "type": "position_update",
                "lat": 37.7750,
                "lng": -122.4195,
                "accuracy": 5.0
            })
            ws.send(pos_msg)
            self.print_info("Sent position update")
        
        try:
            self.ws_connection = websocket.WebSocketApp(
                ws_url,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            
            # Run WebSocket in a thread
            ws_thread = threading.Thread(target=self.ws_connection.run_forever)
            ws_thread.daemon = True
            ws_thread.start()
            
            # Keep connection open for 5 seconds
            time.sleep(5)
            
            # Close connection
            if self.ws_connection:
                self.ws_connection.close()
            
        except Exception as e:
            self.print_error(f"WebSocket test failed: {e}")
    
    def run_full_test_suite(self):
        """Run complete test suite"""
        self.print_header("URBAN ESPIONAGE API TEST SUITE")
        
        print(f"{Colors.MAGENTA}This will test all major API endpoints.{Colors.RESET}")
        print(f"{Colors.MAGENTA}Make sure the backend is running at {BASE_URL}{Colors.RESET}\n")
        
        input("Press Enter to start testing...")
        
        # 1. Create a game
        game = self.test_create_game()
        if not game:
            self.print_error("Cannot continue without creating a game")
            return
        
        time.sleep(1)
        
        # 2. Join the game with additional players
        players = []
        for i in range(3):
            player = self.test_join_game()
            if player:
                players.append(player)
            time.sleep(0.5)
        
        # 3. Start the game
        if len(players) >= 1:
            self.test_start_game()
            time.sleep(1)
        else:
            self.print_error("Not enough players to start game")
        
        # 4. Update positions
        if self.current_player:
            for _ in range(3):
                self.test_update_position()
                time.sleep(0.5)
        
        # 5. Get events
        self.test_get_events()
        time.sleep(1)
        
        # 6. Test WebSocket
        self.test_websocket_connection()
        
        # Summary
        self.print_header("TEST SUMMARY")
        if self.current_game:
            self.print_success(f"Game Code: {self.current_game['code']}")
            self.print_info("You can use this code to test from another client")
            self.print_info(f"API endpoints are available at: {API_URL}")
            self.print_info(f"WebSocket endpoint: {WS_URL}/game/{self.current_game['code']}/")
    
    def interactive_menu(self):
        """Interactive testing menu"""
        while True:
            self.print_header("INTERACTIVE API TESTER")
            print("1. Create new game")
            print("2. Join existing game")
            print("3. Start current game")
            print("4. Update player position")
            print("5. Get game events")
            print("6. Test WebSocket connection")
            print("7. Run full test suite")
            print("8. Show current game info")
            print("0. Exit")
            
            choice = input("\nSelect option: ")
            
            if choice == "1":
                self.test_create_game()
            elif choice == "2":
                code = input("Enter game code (or press Enter to use current): ")
                self.test_join_game(code if code else None)
            elif choice == "3":
                self.test_start_game()
            elif choice == "4":
                self.test_update_position()
            elif choice == "5":
                self.test_get_events()
            elif choice == "6":
                self.test_websocket_connection()
            elif choice == "7":
                self.run_full_test_suite()
            elif choice == "8":
                if self.current_game:
                    self.print_header("Current Game Info")
                    self.print_json(self.current_game)
                else:
                    self.print_error("No current game")
            elif choice == "0":
                break
            else:
                self.print_error("Invalid option")
            
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    import sys
    
    # Check for websocket-client library
    try:
        import websocket
    except ImportError:
        print("Please install websocket-client: pip install websocket-client")
        sys.exit(1)
    
    tester = UrbanEspionageAPITester()
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/api/")
        print(f"{Colors.GREEN}✓ Backend is running at {BASE_URL}{Colors.RESET}")
    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED}✗ Cannot connect to backend at {BASE_URL}")
        print(f"Please make sure the backend is running with: docker-compose up{Colors.RESET}")
        sys.exit(1)
    
    # Run interactive menu
    tester.interactive_menu()
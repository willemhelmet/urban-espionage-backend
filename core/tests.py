from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
import json
import asyncio

from .models import Game, Player, Zone, Event, ItemSpawn, PlayerInventory
from .consumers import GameConsumer


class GameModelTest(TestCase):
    """Test Game model"""
    
    def setUp(self):
        self.host_player = Player.objects.create(
            name="Host Player",
            avatar_url="http://example.com/avatar.png"
        )
    
    def test_game_creation(self):
        """Test creating a game with auto-generated code"""
        game = Game.objects.create(
            host=self.host_player,
            home_base_lat=37.7749,
            home_base_lng=-122.4194,
            map_radius=1000,
            max_players=20
        )
        
        self.assertEqual(len(game.code), 6)
        self.assertEqual(game.status, 'lobby')
        self.assertEqual(game.host, self.host_player)
        self.assertIsNotNone(game.created_at)
    
    def test_unique_game_codes(self):
        """Test that game codes are unique"""
        games = []
        for i in range(10):
            game = Game.objects.create(
                host=self.host_player,
                home_base_lat=37.7749 + i * 0.001,
                home_base_lng=-122.4194
            )
            games.append(game)
        
        codes = [g.code for g in games]
        self.assertEqual(len(codes), len(set(codes)))  # All codes should be unique


class PlayerModelTest(TestCase):
    """Test Player model"""
    
    def setUp(self):
        self.host_player = Player.objects.create(name="Host")
        self.game = Game.objects.create(
            host=self.host_player,
            home_base_lat=37.7749,
            home_base_lng=-122.4194
        )
    
    def test_player_creation(self):
        """Test creating a player"""
        player = Player.objects.create(
            name="Test Player",
            game=self.game,
            team='blue'
        )
        
        self.assertEqual(player.name, "Test Player")
        self.assertEqual(player.team, 'blue')
        self.assertTrue(player.is_alive)
        self.assertTrue(player.is_online)
        self.assertEqual(player.visibility, 'active')
    
    def test_player_inventory(self):
        """Test player inventory system"""
        player = Player.objects.create(
            name="Test Player",
            game=self.game
        )
        
        inventory = PlayerInventory.objects.create(player=player)
        self.assertIsNone(inventory.item)
        
        # Add an item
        item = ItemSpawn.objects.create(
            game=self.game,
            item_type='dagger',
            position_lat=37.7749,
            position_lng=-122.4194
        )
        
        inventory.item = item
        inventory.save()
        
        self.assertEqual(inventory.item, item)


class GameAPITest(APITestCase):
    """Test Game API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
    
    def test_create_game(self):
        """Test creating a new game via API"""
        data = {
            'host_name': 'Test Host',
            'home_base_lat': 37.7749,
            'home_base_lng': -122.4194,
            'map_radius': 1000,
            'max_players': 20,
            'game_duration': 60,
            'red_team_ratio': 0.25,
            'tasks_to_win': 5,
            'failures_to_lose': 2
        }
        
        response = self.client.post('/api/games/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('code', response.data)
        self.assertEqual(len(response.data['code']), 6)
        self.assertEqual(response.data['status'], 'lobby')
        
        # Verify game was created in database
        game = Game.objects.get(code=response.data['code'])
        self.assertEqual(game.home_base_lat, 37.7749)
        
        # Verify home base zone was created
        home_base = Zone.objects.get(game=game, type='home_base')
        self.assertEqual(home_base.position_lat, 37.7749)
    
    def test_join_game(self):
        """Test joining a game"""
        # Create a game first
        host = Player.objects.create(name="Host")
        game = Game.objects.create(
            host=host,
            home_base_lat=37.7749,
            home_base_lng=-122.4194
        )
        host.game = game
        host.save()
        
        # Join the game
        data = {
            'player_name': 'New Player',
            'avatar_url': 'http://example.com/avatar.png'
        }
        
        response = self.client.post(f'/api/games/{game.code}/join/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Player')
        
        # Verify player was added to game
        self.assertEqual(game.players.count(), 2)  # Host + new player
    
    def test_cannot_join_started_game(self):
        """Test that players cannot join a game that has started"""
        host = Player.objects.create(name="Host")
        game = Game.objects.create(
            host=host,
            home_base_lat=37.7749,
            home_base_lng=-122.4194,
            status='active'
        )
        
        data = {'player_name': 'Late Player'}
        response = self.client.post(f'/api/games/{game.code}/join/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Game has already started')
    
    def test_start_game(self):
        """Test starting a game"""
        # Create game with multiple players
        host = Player.objects.create(name="Host")
        game = Game.objects.create(
            host=host,
            home_base_lat=37.7749,
            home_base_lng=-122.4194
        )
        host.game = game
        host.save()
        
        # Add more players
        for i in range(3):
            Player.objects.create(
                name=f"Player {i}",
                game=game
            )
        
        response = self.client.post(f'/api/games/{game.code}/start/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify game status changed
        game.refresh_from_db()
        self.assertEqual(game.status, 'active')
        self.assertIsNotNone(game.started_at)
        
        # Verify teams were assigned
        blue_team = game.players.filter(team='blue').count()
        red_team = game.players.filter(team='red').count()
        self.assertGreater(blue_team, 0)
        self.assertGreater(red_team, 0)
        self.assertEqual(blue_team + red_team, 4)
        
        # Verify zones and items were generated
        self.assertGreater(Zone.objects.filter(game=game).count(), 1)
        self.assertGreater(ItemSpawn.objects.filter(game=game).count(), 0)


class PlayerAPITest(APITestCase):
    """Test Player API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create a game with a player
        self.host = Player.objects.create(name="Host")
        self.game = Game.objects.create(
            host=self.host,
            home_base_lat=37.7749,
            home_base_lng=-122.4194
        )
        
        self.player = Player.objects.create(
            name="Test Player",
            game=self.game,
            position_lat=37.7749,
            position_lng=-122.4194
        )
    
    def test_update_position(self):
        """Test updating player position"""
        data = {
            'lat': 37.7750,
            'lng': -122.4195,
            'accuracy': 5.0
        }
        
        response = self.client.post(
            f'/api/players/{self.player.id}/update_position/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify position was updated
        self.player.refresh_from_db()
        self.assertEqual(self.player.position_lat, 37.7750)
        self.assertEqual(self.player.position_lng, -122.4195)
        self.assertEqual(self.player.visibility, 'active')
        
        # Verify event was logged
        event = Event.objects.filter(
            game=self.game,
            type='player_moved',
            player=self.player
        ).first()
        self.assertIsNotNone(event)
    
    def test_pickup_item(self):
        """Test picking up an item"""
        # Create an item near the player
        item = ItemSpawn.objects.create(
            game=self.game,
            item_type='dagger',
            position_lat=37.7749,
            position_lng=-122.4194,
            available=True
        )
        
        # Create inventory for player
        PlayerInventory.objects.create(player=self.player)
        
        data = {'item_id': str(item.id)}
        
        response = self.client.post(
            f'/api/players/{self.player.id}/pickup_item/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify item was picked up
        item.refresh_from_db()
        self.assertFalse(item.available)
        self.assertEqual(item.collected_by, self.player)
        
        # Verify inventory was updated
        inventory = self.player.inventory
        self.assertEqual(inventory.item, item)
    
    def test_cannot_pickup_distant_item(self):
        """Test that players cannot pick up items that are too far away"""
        # Create an item far from the player
        item = ItemSpawn.objects.create(
            game=self.game,
            item_type='armor',
            position_lat=37.8000,  # Far away
            position_lng=-122.4000,
            available=True,
            pickup_radius=10
        )
        
        PlayerInventory.objects.create(player=self.player)
        
        data = {'item_id': str(item.id)}
        
        response = self.client.post(
            f'/api/players/{self.player.id}/pickup_item/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Too far from item')


class EventAPITest(APITestCase):
    """Test Event API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create a game
        self.host = Player.objects.create(name="Host")
        self.game = Game.objects.create(
            host=self.host,
            home_base_lat=37.7749,
            home_base_lng=-122.4194
        )
        
        # Create some events
        Event.objects.create(
            game=self.game,
            type='player_joined',
            player=self.host,
            message='Host joined the game'
        )
        
        Event.objects.create(
            game=self.game,
            type='game_started',
            message='Game started'
        )
    
    def test_get_game_events(self):
        """Test retrieving events for a game"""
        response = self.client.get(f'/api/events/?game_code={self.game.code}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # Verify events are in reverse chronological order
        first_event = response.data['results'][0]
        self.assertEqual(first_event['type'], 'game_started')


class WebSocketTest(TransactionTestCase):
    """Test WebSocket connections"""
    
    async def test_websocket_connection(self):
        """Test establishing WebSocket connection"""
        # Create a game
        host = await database_sync_to_async(Player.objects.create)(name="Host")
        game = await database_sync_to_async(Game.objects.create)(
            host=host,
            home_base_lat=37.7749,
            home_base_lng=-122.4194
        )
        
        # Create WebSocket communicator
        communicator = WebsocketCommunicator(
            GameConsumer.as_asgi(),
            f"/ws/game/{game.code}/"
        )
        
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        
        # Send authentication message
        await communicator.send_json_to({
            'type': 'authenticate',
            'player_id': str(host.id)
        })
        
        # Should receive confirmation (in real implementation)
        # For now, just disconnect
        await communicator.disconnect()
    
    async def test_position_broadcast(self):
        """Test position update broadcasting"""
        # Create game with two players
        host = await database_sync_to_async(Player.objects.create)(name="Host")
        game = await database_sync_to_async(Game.objects.create)(
            host=host,
            home_base_lat=37.7749,
            home_base_lng=-122.4194
        )
        
        player2 = await database_sync_to_async(Player.objects.create)(
            name="Player 2",
            game=game
        )
        
        # Connect first player
        comm1 = WebsocketCommunicator(
            GameConsumer.as_asgi(),
            f"/ws/game/{game.code}/"
        )
        await comm1.connect()
        
        # Connect second player
        comm2 = WebsocketCommunicator(
            GameConsumer.as_asgi(),
            f"/ws/game/{game.code}/"
        )
        await comm2.connect()
        
        # Player 1 sends position update
        await comm1.send_json_to({
            'type': 'position_update',
            'lat': 37.7750,
            'lng': -122.4195
        })
        
        # Player 2 should receive the update
        # (In full implementation, would check received message)
        
        await comm1.disconnect()
        await comm2.disconnect()

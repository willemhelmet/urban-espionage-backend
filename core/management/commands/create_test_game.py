from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
import random
import math

from core.models import (
    Game, Player, Zone, Event, ItemSpawn, 
    PlayerInventory, Task
)


class Command(BaseCommand):
    help = 'Creates a test game with sample data for development'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--players',
            type=int,
            default=8,
            help='Number of players to create (default: 8)'
        )
        parser.add_argument(
            '--lat',
            type=float,
            default=37.7749,
            help='Home base latitude (default: 37.7749 - San Francisco)'
        )
        parser.add_argument(
            '--lng',
            type=float,
            default=-122.4194,
            help='Home base longitude (default: -122.4194 - San Francisco)'
        )
        parser.add_argument(
            '--radius',
            type=int,
            default=1000,
            help='Map radius in meters (default: 1000)'
        )
        parser.add_argument(
            '--start',
            action='store_true',
            help='Start the game immediately'
        )
    
    @transaction.atomic
    def handle(self, *args, **options):
        num_players = options['players']
        home_lat = options['lat']
        home_lng = options['lng']
        map_radius = options['radius']
        start_game = options['start']
        
        self.stdout.write(self.style.SUCCESS('Creating test game...'))
        
        # Create host player first (without game)
        host = Player.objects.create(
            name="TestHost",
            avatar_url="https://api.dicebear.com/7.x/avataaars/svg?seed=host"
        )
        
        # Create game
        game = Game.objects.create(
            host=host,
            home_base_lat=home_lat,
            home_base_lng=home_lng,
            map_radius=map_radius,
            max_players=20,
            game_duration=60,
            red_team_ratio=0.3,
            tasks_to_win=5,
            failures_to_lose=2
        )
        
        # Update host with game reference
        host.game = game
        host.save()
        
        self.stdout.write(f"Created game with code: {self.style.WARNING(game.code)}")
        
        # Create home base zone
        Zone.objects.create(
            game=game,
            type='home_base',
            position_lat=home_lat,
            position_lng=home_lng,
            radius=50
        )
        
        # Create additional players
        player_names = [
            "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", 
            "Grace", "Henry", "Iris", "Jack", "Kate", "Leo",
            "Maya", "Noah", "Olivia", "Peter", "Quinn", "Rose"
        ]
        
        players = [host]
        for i in range(min(num_players - 1, len(player_names))):
            player = Player.objects.create(
                name=player_names[i],
                game=game,
                avatar_url=f"https://api.dicebear.com/7.x/avataaars/svg?seed={player_names[i]}"
            )
            PlayerInventory.objects.create(player=player)
            players.append(player)
            
            # Log join event
            Event.objects.create(
                game=game,
                type='player_joined',
                player=player,
                message=f"{player.name} joined the game"
            )
        
        self.stdout.write(f"Created {len(players)} players")
        
        if start_game:
            # Assign teams
            red_count = max(1, int(len(players) * game.red_team_ratio))
            red_players = random.sample(players, red_count)
            
            for player in players:
                if player in red_players:
                    player.team = 'red'
                else:
                    player.team = 'blue'
                player.save()
            
            blue_count = len(players) - red_count
            self.stdout.write(f"Assigned teams: {blue_count} blue, {red_count} red")
            
            # Generate game content
            self._generate_zones(game, home_lat, home_lng, map_radius)
            self._generate_items(game, home_lat, home_lng, map_radius)
            self._generate_sample_tasks(game)
            
            # Set random positions for players
            for player in players:
                lat, lng = self._random_position(home_lat, home_lng, map_radius * 0.5)
                player.position_lat = lat
                player.position_lng = lng
                player.visibility = random.choice(['active', 'recent', 'dark'])
                player.last_seen = timezone.now()
                player.save()
            
            # Update game status
            game.status = 'active'
            game.started_at = timezone.now()
            game.save()
            
            # Log start event
            Event.objects.create(
                game=game,
                type='game_started',
                message=f"Game started with {len(players)} players"
            )
            
            self.stdout.write(self.style.SUCCESS('Game started!'))
        
        # Print summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('TEST GAME CREATED SUCCESSFULLY'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(f"Game Code: {self.style.WARNING(game.code)}")
        self.stdout.write(f"Status: {game.status}")
        self.stdout.write(f"Players: {len(players)}")
        self.stdout.write(f"Home Base: ({home_lat}, {home_lng})")
        self.stdout.write(f"Map Radius: {map_radius}m")
        
        if start_game:
            self.stdout.write(f"\nZones: {Zone.objects.filter(game=game).count()}")
            self.stdout.write(f"Items: {ItemSpawn.objects.filter(game=game).count()}")
            self.stdout.write(f"Tasks: {Task.objects.filter(game=game).count()}")
        
        self.stdout.write(self.style.SUCCESS('\nAPI Endpoints:'))
        self.stdout.write(f"  GET  /api/games/{game.code}/")
        self.stdout.write(f"  POST /api/games/{game.code}/join/")
        if not start_game:
            self.stdout.write(f"  POST /api/games/{game.code}/start/")
        
        self.stdout.write(self.style.SUCCESS('\nWebSocket:'))
        self.stdout.write(f"  ws://localhost:8001/ws/game/{game.code}/")
        
        self.stdout.write(self.style.SUCCESS('\nPlayer IDs:'))
        for player in players[:5]:
            team_color = self.style.ERROR if player.team == 'red' else self.style.WARNING
            team_label = f" [{team_color(player.team)}]" if player.team else ""
            self.stdout.write(f"  {player.name}: {player.id}{team_label}")
    
    def _random_position(self, center_lat, center_lng, radius_meters):
        """Generate random position within radius"""
        radius_deg = radius_meters / 111000
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0.3, 1) * radius_deg
        
        lat = center_lat + distance * math.cos(angle)
        lng = center_lng + distance * math.sin(angle)
        
        return lat, lng
    
    def _generate_zones(self, game, center_lat, center_lng, radius):
        """Generate task and reviver zones"""
        # Task zones
        for i in range(random.randint(4, 6)):
            lat, lng = self._random_position(center_lat, center_lng, radius)
            Zone.objects.create(
                game=game,
                type='task',
                position_lat=lat,
                position_lng=lng,
                radius=30,
                metadata={'zone_name': f'Task Zone {i+1}'}
            )
        
        # Reviver zones
        for i in range(2):
            lat, lng = self._random_position(center_lat, center_lng, radius)
            Zone.objects.create(
                game=game,
                type='reviver',
                position_lat=lat,
                position_lng=lng,
                radius=20,
                metadata={'zone_name': f'Reviver Zone {i+1}'}
            )
    
    def _generate_items(self, game, center_lat, center_lng, radius):
        """Generate item spawns"""
        item_types = [
            ('dagger', 3),
            ('armor', 2),
            ('emp', 2),
            ('camera', 2),
            ('mask', 1),
            ('invisibility_cloak', 2),
            ('poison', 2),
            ('motion_sensor', 2),
            ('decoy', 2),
            ('time_bomb', 1),
            ('land_mine', 2)
        ]
        
        for item_type, count in item_types:
            for _ in range(count):
                lat, lng = self._random_position(center_lat, center_lng, radius)
                ItemSpawn.objects.create(
                    game=game,
                    item_type=item_type,
                    position_lat=lat,
                    position_lng=lng,
                    pickup_radius=15
                )
    
    def _generate_sample_tasks(self, game):
        """Generate sample tasks"""
        task_zones = Zone.objects.filter(game=game, type='task')
        
        if task_zones.count() >= 2:
            # Create a capture objective task
            task1 = Task.objects.create(
                game=game,
                type='capture_objective',
                status='pending',
                metadata={
                    'objective_name': 'Alpha Point',
                    'time_limit': 600
                }
            )
            task1.zones.add(task_zones[0])
            
            # Create a password chain task
            task2 = Task.objects.create(
                game=game,
                type='password_chain',
                status='pending',
                metadata={
                    'password_fragments': ['ALPHA', 'BRAVO', 'CHARLIE'],
                    'final_password': 'ALPHABRAVOCHARLIE'
                }
            )
            task2.zones.add(task_zones[1])
            if task_zones.count() >= 3:
                task2.zones.add(task_zones[2])
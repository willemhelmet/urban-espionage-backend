from django.utils import timezone
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import random

from .models import Game, Player, Zone, Event, ItemSpawn, PlayerInventory, Task
from .serializers import (
    GameListSerializer, GameDetailSerializer, CreateGameSerializer,
    JoinGameSerializer, PlayerSerializer, ZoneSerializer, EventSerializer,
    ItemSpawnSerializer, TaskSerializer, UpdatePositionSerializer,
    PickupItemSerializer, UseItemSerializer
)


class GameViewSet(viewsets.ModelViewSet):
    """API viewset for games"""
    queryset = Game.objects.all()
    permission_classes = [AllowAny]
    lookup_field = 'code'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return GameListSerializer
        elif self.action == 'create':
            return CreateGameSerializer
        elif self.action == 'join':
            return JoinGameSerializer
        return GameDetailSerializer
    
    @transaction.atomic
    def create(self, request):
        """Create a new game lobby"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create the host player first
        host_player = Player.objects.create(
            name=request.data.get('host_name', 'Host'),
            avatar_url=request.data.get('avatar_url', '')
        )
        
        # Create the game with host
        game = Game.objects.create(
            host=host_player,
            **serializer.validated_data
        )
        
        # Update host player with game reference
        host_player.game = game
        host_player.save()
        
        # Create home base zone
        Zone.objects.create(
            game=game,
            type='home_base',
            position_lat=game.home_base_lat,
            position_lng=game.home_base_lng,
            radius=50
        )
        
        # Log event
        Event.objects.create(
            game=game,
            type='player_joined',
            player=host_player,
            message=f"{host_player.name} created the game"
        )
        
        return Response(
            GameDetailSerializer(game).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def join(self, request, code=None):
        """Join a game lobby"""
        game = self.get_object()
        
        if game.status != 'lobby':
            return Response(
                {'error': 'Game has already started'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if game.players.count() >= game.max_players:
            return Response(
                {'error': 'Game is full'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = JoinGameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check if name is already taken
        if game.players.filter(name=serializer.validated_data['player_name']).exists():
            return Response(
                {'error': 'Name already taken'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create player
        player = Player.objects.create(
            game=game,
            name=serializer.validated_data['player_name'],
            avatar_url=serializer.validated_data.get('avatar_url', '')
        )
        
        # Create inventory
        PlayerInventory.objects.create(player=player)
        
        # Log event
        Event.objects.create(
            game=game,
            type='player_joined',
            player=player,
            message=f"{player.name} joined the game"
        )
        
        # Broadcast to all players in the game via WebSocket
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'game_{game.code}',
            {
                'type': 'player_joined',
                'player': PlayerSerializer(player).data
            }
        )
        
        return Response(
            PlayerSerializer(player).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def start(self, request, code=None):
        """Start the game (host only)"""
        game = self.get_object()
        
        if game.status != 'lobby':
            return Response(
                {'error': 'Game has already started'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if request is from host (simplified for now)
        # In production, use proper authentication
        
        if game.players.count() < 2:
            return Response(
                {'error': 'Need at least 2 players to start'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Assign teams
        players = list(game.players.all())
        red_count = max(1, int(len(players) * game.red_team_ratio))
        red_players = random.sample(players, red_count)
        
        for player in players:
            if player in red_players:
                player.team = 'red'
            else:
                player.team = 'blue'
            player.save()
        
        # Generate zones and items
        self._generate_game_content(game)
        
        # Update game status
        game.status = 'active'
        game.started_at = timezone.now()
        game.save()
        
        # Log event
        Event.objects.create(
            game=game,
            type='game_started',
            message=f"Game started with {len(players)} players"
        )
        
        # Broadcast game started to all players via WebSocket
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'game_{game.code}',
            {
                'type': 'game_started',
                'game': GameDetailSerializer(game).data
            }
        )
        
        return Response(
            GameDetailSerializer(game).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def leave(self, request, code=None):
        """Leave a game"""
        game = self.get_object()
        player_id = request.data.get('player_id')
        
        try:
            player = game.players.get(id=player_id)
        except Player.DoesNotExist:
            return Response(
                {'error': 'Player not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Store player info before potential deletion
        player_name = player.name
        player_id_str = str(player.id)
        
        # If game hasn't started, remove player completely
        # If game is active, just mark them as offline
        if game.status == 'lobby':
            # Check if this is the host leaving
            if player.id == game.host_id:
                # Transfer host to another player if any exist
                remaining_players = game.players.exclude(id=player.id)
                if remaining_players.exists():
                    game.host_id = remaining_players.first().id
                    game.save()
            
            # Log event BEFORE deleting the player
            Event.objects.create(
                game=game,
                type='player_left',
                player=player,
                message=f"{player_name} left the game"
            )
            
            player.delete()  # Remove player from game entirely
        else:
            player.left_at = timezone.now()
            player.is_online = False
            player.visibility = 'dark'
            player.save()
            
            # Log event after marking as offline
            Event.objects.create(
                game=game,
                type='player_left',
                player=player,
                message=f"{player_name} left the game"
            )
        
        # Broadcast to all players in the game via WebSocket
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'game_{game.code}',
            {
                'type': 'player_left',
                'player_id': player_id_str
            }
        )
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def _generate_game_content(self, game):
        """Generate zones, items, and tasks for the game"""
        import math
        
        # Helper to generate random positions within map radius
        def random_position_in_radius(center_lat, center_lng, radius_meters):
            # Convert radius to degrees (approximate)
            radius_deg = radius_meters / 111000  # 1 degree ≈ 111km
            
            # Generate random angle and distance
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0.3, 1) * radius_deg
            
            # Calculate new position
            lat = center_lat + distance * math.cos(angle)
            lng = center_lng + distance * math.sin(angle)
            
            return lat, lng
        
        # Generate task zones (3-5 zones)
        for i in range(random.randint(3, 5)):
            lat, lng = random_position_in_radius(
                game.home_base_lat,
                game.home_base_lng,
                game.map_radius
            )
            Zone.objects.create(
                game=game,
                type='task',
                position_lat=lat,
                position_lng=lng,
                radius=30
            )
        
        # Generate reviver zones (2 zones)
        for i in range(2):
            lat, lng = random_position_in_radius(
                game.home_base_lat,
                game.home_base_lng,
                game.map_radius
            )
            Zone.objects.create(
                game=game,
                type='reviver',
                position_lat=lat,
                position_lng=lng,
                radius=20
            )
        
        # Generate item spawns (10-15 items)
        item_types = [
            'emp', 'camera', 'dagger', 'mask', 'armor',
            'invisibility_cloak', 'poison', 'motion_sensor', 'decoy'
        ]
        
        for i in range(random.randint(10, 15)):
            lat, lng = random_position_in_radius(
                game.home_base_lat,
                game.home_base_lng,
                game.map_radius
            )
            ItemSpawn.objects.create(
                game=game,
                item_type=random.choice(item_types),
                position_lat=lat,
                position_lng=lng
            )


class PlayerViewSet(viewsets.ModelViewSet):
    """API viewset for players"""
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [AllowAny]
    
    @action(detail=True, methods=['post'])
    def update_position(self, request, pk=None):
        """Update player position"""
        player = self.get_object()
        serializer = UpdatePositionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        player.position_lat = serializer.validated_data['lat']
        player.position_lng = serializer.validated_data['lng']
        player.position_accuracy = serializer.validated_data.get('accuracy')
        player.visibility = 'active'
        player.last_seen = timezone.now()
        player.save()
        
        # Log movement event (throttle this in production)
        Event.objects.create(
            game=player.game,
            type='player_moved',
            player=player,
            message=f"{player.name} moved",
            position_lat=player.position_lat,
            position_lng=player.position_lng,
            visibility='team'
        )
        
        return Response(PlayerSerializer(player).data)
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def pickup_item(self, request, pk=None):
        """Pick up an item"""
        player = self.get_object()
        serializer = PickupItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            item = ItemSpawn.objects.get(
                id=serializer.validated_data['item_id'],
                game=player.game,
                available=True
            )
        except ItemSpawn.DoesNotExist:
            return Response(
                {'error': 'Item not found or not available'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check proximity (simplified - in production use PostGIS)
        # This is a rough approximation
        distance = ((player.position_lat - item.position_lat) ** 2 + 
                   (player.position_lng - item.position_lng) ** 2) ** 0.5
        max_distance = item.pickup_radius / 111000  # Convert meters to degrees
        
        if distance > max_distance:
            return Response(
                {'error': 'Too far from item'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update inventory
        inventory, _ = PlayerInventory.objects.get_or_create(player=player)
        
        # Drop current item if holding one
        if inventory.item:
            old_item = inventory.item
            old_item.available = True
            old_item.position_lat = player.position_lat
            old_item.position_lng = player.position_lng
            old_item.dropped_by = player
            old_item.save()
        
        # Pick up new item
        inventory.item = item
        inventory.save()
        
        item.available = False
        item.collected_by = player
        item.collected_at = timezone.now()
        item.save()
        
        # Log event
        Event.objects.create(
            game=player.game,
            type='item_picked',
            player=player,
            message=f"{player.name} picked up {item.item_type}",
            position_lat=player.position_lat,
            position_lng=player.position_lng
        )
        
        return Response(PlayerSerializer(player).data)
    
    @action(detail=True, methods=['post'])
    def use_item(self, request, pk=None):
        """Use an item"""
        player = self.get_object()
        serializer = UseItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get player's current item
        try:
            inventory = player.inventory
            if not inventory.item:
                return Response(
                    {'error': 'No item to use'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except PlayerInventory.DoesNotExist:
            return Response(
                {'error': 'No inventory'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        item = inventory.item
        
        # Handle item usage (simplified - expand based on item type)
        # This is a placeholder - implement full item logic later
        
        # Clear inventory
        inventory.item = None
        inventory.save()
        
        # Log event
        Event.objects.create(
            game=player.game,
            type='item_used',
            player=player,
            message=f"{player.name} used {item.item_type}",
            position_lat=player.position_lat,
            position_lng=player.position_lng
        )
        
        return Response({'message': f'Used {item.item_type}'})


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """API viewset for game events"""
    serializer_class = EventSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        game_code = self.request.query_params.get('game_code')
        if game_code:
            return Event.objects.filter(game__code=game_code)
        return Event.objects.none()


class ZoneViewSet(viewsets.ReadOnlyModelViewSet):
    """API viewset for zones"""
    serializer_class = ZoneSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        game_code = self.request.query_params.get('game_code')
        if game_code:
            return Zone.objects.filter(game__code=game_code, active=True)
        return Zone.objects.none()


class ItemSpawnViewSet(viewsets.ReadOnlyModelViewSet):
    """API viewset for item spawns"""
    serializer_class = ItemSpawnSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        game_code = self.request.query_params.get('game_code')
        if game_code:
            return ItemSpawn.objects.filter(game__code=game_code, available=True)
        return ItemSpawn.objects.none()


class TaskViewSet(viewsets.ModelViewSet):
    """API viewset for tasks"""
    serializer_class = TaskSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        game_code = self.request.query_params.get('game_code')
        if game_code:
            return Task.objects.filter(game__code=game_code)
        return Task.objects.none()

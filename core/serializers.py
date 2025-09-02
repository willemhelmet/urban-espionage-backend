from rest_framework import serializers
from .models import (
    Game, Player, Zone, Event, ItemSpawn, PlayerInventory,
    DeployedItem, StatusEffect, Task
)


class PlayerSerializer(serializers.ModelSerializer):
    """Serializer for Player model"""
    position = serializers.SerializerMethodField()
    death_position = serializers.SerializerMethodField()
    current_item = serializers.SerializerMethodField()
    
    class Meta:
        model = Player
        fields = [
            'id', 'name', 'avatar_url', 'team', 'is_alive', 'is_online',
            'visibility', 'position', 'position_accuracy', 'last_seen',
            'death_time', 'death_position', 'current_item', 'joined_at'
        ]
        read_only_fields = ['id', 'joined_at', 'last_seen']
    
    def get_position(self, obj):
        if obj.position_lat and obj.position_lng:
            return {
                'lat': obj.position_lat,
                'lng': obj.position_lng
            }
        return None
    
    def get_death_position(self, obj):
        if obj.death_position_lat and obj.death_position_lng:
            return {
                'lat': obj.death_position_lat,
                'lng': obj.death_position_lng
            }
        return None
    
    def get_current_item(self, obj):
        if hasattr(obj, 'inventory') and obj.inventory.item:
            return {
                'id': str(obj.inventory.item.id),
                'type': obj.inventory.item.item_type
            }
        return None


class GameListSerializer(serializers.ModelSerializer):
    """Serializer for game list view"""
    player_count = serializers.SerializerMethodField()
    host_name = serializers.CharField(source='host.name', read_only=True)
    
    class Meta:
        model = Game
        fields = [
            'id', 'code', 'status', 'host_name', 'player_count',
            'max_players', 'created_at'
        ]
    
    def get_player_count(self, obj):
        return obj.players.count()


class GameDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Game model"""
    players = PlayerSerializer(many=True, read_only=True)
    home_base = serializers.SerializerMethodField()
    config = serializers.SerializerMethodField()
    
    class Meta:
        model = Game
        fields = [
            'id', 'code', 'status', 'home_base', 'config',
            'tasks_completed', 'tasks_failed', 'winner',
            'players', 'created_at', 'started_at', 'ended_at'
        ]
        read_only_fields = [
            'id', 'code', 'tasks_completed', 'tasks_failed',
            'winner', 'created_at', 'started_at', 'ended_at'
        ]
    
    def get_home_base(self, obj):
        return {
            'lat': obj.home_base_lat,
            'lng': obj.home_base_lng
        }
    
    def get_config(self, obj):
        return {
            'map_radius': obj.map_radius,
            'max_players': obj.max_players,
            'game_duration': obj.game_duration,
            'red_team_ratio': obj.red_team_ratio,
            'tasks_to_win': obj.tasks_to_win,
            'failures_to_lose': obj.failures_to_lose
        }


class CreateGameSerializer(serializers.ModelSerializer):
    """Serializer for creating a new game"""
    home_base_lat = serializers.FloatField(required=True)
    home_base_lng = serializers.FloatField(required=True)
    
    class Meta:
        model = Game
        fields = [
            'home_base_lat', 'home_base_lng', 'map_radius',
            'max_players', 'game_duration', 'red_team_ratio',
            'tasks_to_win', 'failures_to_lose'
        ]


class JoinGameSerializer(serializers.Serializer):
    """Serializer for joining a game"""
    player_name = serializers.CharField(max_length=100)
    avatar_url = serializers.URLField(required=False, allow_blank=True)


class ZoneSerializer(serializers.ModelSerializer):
    """Serializer for Zone model"""
    position = serializers.SerializerMethodField()
    
    class Meta:
        model = Zone
        fields = [
            'id', 'type', 'position', 'radius', 'active',
            'metadata', 'expires_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_position(self, obj):
        return {
            'lat': obj.position_lat,
            'lng': obj.position_lng
        }


class ItemSpawnSerializer(serializers.ModelSerializer):
    """Serializer for ItemSpawn model"""
    position = serializers.SerializerMethodField()
    
    class Meta:
        model = ItemSpawn
        fields = [
            'id', 'item_type', 'position', 'pickup_radius',
            'available', 'collected_by', 'collected_at'
        ]
        read_only_fields = ['id', 'collected_by', 'collected_at']
    
    def get_position(self, obj):
        return {
            'lat': obj.position_lat,
            'lng': obj.position_lng
        }


class EventSerializer(serializers.ModelSerializer):
    """Serializer for Event model"""
    player_name = serializers.CharField(source='player.name', read_only=True)
    position = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = [
            'id', 'type', 'player_name', 'message', 'visibility',
            'position', 'data', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_position(self, obj):
        if obj.position_lat and obj.position_lng:
            return {
                'lat': obj.position_lat,
                'lng': obj.position_lng
            }
        return None


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model"""
    zones = ZoneSerializer(many=True, read_only=True)
    participating_players = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True
    )
    
    class Meta:
        model = Task
        fields = [
            'id', 'type', 'status', 'zones', 'participating_players',
            'progress', 'metadata', 'created_at', 'completed_at', 'failed_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'completed_at', 'failed_at'
        ]


class UpdatePositionSerializer(serializers.Serializer):
    """Serializer for updating player position"""
    lat = serializers.FloatField(required=True)
    lng = serializers.FloatField(required=True)
    accuracy = serializers.FloatField(required=False)


class PickupItemSerializer(serializers.Serializer):
    """Serializer for picking up an item"""
    item_id = serializers.UUIDField(required=True)


class UseItemSerializer(serializers.Serializer):
    """Serializer for using an item"""
    target_player_id = serializers.UUIDField(required=False)
    target_position_lat = serializers.FloatField(required=False)
    target_position_lng = serializers.FloatField(required=False)
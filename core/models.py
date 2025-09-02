import uuid
import random
import string
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


def generate_game_code():
    """Generate a 6-character alphanumeric game code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


class Game(models.Model):
    """Main game instance"""
    STATUS_CHOICES = [
        ('lobby', 'Lobby'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=6, unique=True, default=generate_game_code)
    host = models.ForeignKey('Player', on_delete=models.CASCADE, related_name='hosted_games')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='lobby')
    
    # Game configuration
    home_base_lat = models.FloatField()
    home_base_lng = models.FloatField()
    map_radius = models.IntegerField(default=1000, help_text="Radius in meters from home base")
    max_players = models.IntegerField(default=20)
    game_duration = models.IntegerField(default=60, help_text="Duration in minutes")
    red_team_ratio = models.FloatField(default=0.25, validators=[MinValueValidator(0.1), MaxValueValidator(0.5)])
    tasks_to_win = models.IntegerField(default=5)
    failures_to_lose = models.IntegerField(default=2)
    
    # Game state
    tasks_completed = models.IntegerField(default=0)
    tasks_failed = models.IntegerField(default=0)
    winner = models.CharField(max_length=10, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Game {self.code} - {self.status}"


class Player(models.Model):
    """Player in a game"""
    TEAM_CHOICES = [
        ('blue', 'Blue Team'),
        ('red', 'Red Team'),
    ]
    
    VISIBILITY_CHOICES = [
        ('active', 'Active'),
        ('recent', 'Recent'),
        ('dark', 'Dark'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    avatar_url = models.URLField(null=True, blank=True)
    
    # Game association
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='players')
    team = models.CharField(max_length=10, choices=TEAM_CHOICES, null=True, blank=True)
    
    # Player state
    is_alive = models.BooleanField(default=True)
    is_online = models.BooleanField(default=True)
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='active')
    
    # Position
    position_lat = models.FloatField(null=True, blank=True)
    position_lng = models.FloatField(null=True, blank=True)
    position_accuracy = models.FloatField(null=True, blank=True)
    last_seen = models.DateTimeField(auto_now=True)
    
    # Death tracking
    death_time = models.DateTimeField(null=True, blank=True)
    death_position_lat = models.FloatField(null=True, blank=True)
    death_position_lng = models.FloatField(null=True, blank=True)
    
    # Timestamps
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['game', 'team', 'name']
        unique_together = [['game', 'name']]
    
    def __str__(self):
        return f"{self.name} ({self.game.code})"


class Zone(models.Model):
    """Game zones (home base, task zones, reviver zones, etc.)"""
    TYPE_CHOICES = [
        ('home_base', 'Home Base'),
        ('task', 'Task Zone'),
        ('item_spawn', 'Item Spawn'),
        ('reviver', 'Reviver Zone'),
        ('emp_field', 'EMP Field'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='zones')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    # Position
    position_lat = models.FloatField()
    position_lng = models.FloatField()
    radius = models.IntegerField(help_text="Radius in meters")
    
    # Metadata
    active = models.BooleanField(default=True)
    created_by = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['game', 'type']
    
    def __str__(self):
        return f"{self.type} zone in {self.game.code}"


class ItemSpawn(models.Model):
    """Items spawned on the map"""
    ITEM_TYPE_CHOICES = [
        ('emp', 'EMP'),
        ('camera', 'Camera'),
        ('time_bomb', 'Time Bomb'),
        ('land_mine', 'Land Mine'),
        ('dagger', 'Dagger'),
        ('mask', 'Mask'),
        ('armor', 'Armor'),
        ('invisibility_cloak', 'Invisibility Cloak'),
        ('poison', 'Poison'),
        ('motion_sensor', 'Motion Sensor'),
        ('decoy', 'Decoy'),
        ('dogtag', 'Dogtag'),
        ('briefcase', 'Briefcase'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=30, choices=ITEM_TYPE_CHOICES)
    
    # Position
    position_lat = models.FloatField()
    position_lng = models.FloatField()
    pickup_radius = models.IntegerField(default=10, help_text="Pickup radius in meters")
    
    # State
    available = models.BooleanField(default=True)
    collected_by = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='collected_items')
    collected_at = models.DateTimeField(null=True, blank=True)
    dropped_by = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='dropped_items')
    respawn_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['game', 'available', 'item_type']
    
    def __str__(self):
        return f"{self.item_type} in {self.game.code}"


class PlayerInventory(models.Model):
    """Single-slot inventory system"""
    player = models.OneToOneField(Player, on_delete=models.CASCADE, related_name='inventory')
    item = models.ForeignKey(ItemSpawn, on_delete=models.SET_NULL, null=True, blank=True)
    picked_up_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.item:
            return f"{self.player.name} has {self.item.item_type}"
        return f"{self.player.name} has no item"


class DeployedItem(models.Model):
    """Items deployed by players (cameras, mines, sensors, etc.)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='deployed_items')
    item_type = models.CharField(max_length=30, choices=ItemSpawn.ITEM_TYPE_CHOICES)
    
    # Position
    position_lat = models.FloatField()
    position_lng = models.FloatField()
    
    # Deployment info
    deployed_by = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='deployed_items')
    deployed_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    
    # Item-specific metadata
    metadata = models.JSONField(default=dict, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.item_type} deployed by {self.deployed_by.name}"


class StatusEffect(models.Model):
    """Status effects on players"""
    TYPE_CHOICES = [
        ('poisoned', 'Poisoned'),
        ('masked', 'Masked'),
        ('invisible', 'Invisible'),
    ]
    
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='status_effects')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    source_player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='inflicted_effects')
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['player', 'expires_at']
    
    def __str__(self):
        return f"{self.player.name} is {self.type}"


class Task(models.Model):
    """Game tasks"""
    TYPE_CHOICES = [
        ('capture_intel', 'Capture Intel'),
        ('defuse_bomb', 'Defuse Bomb'),
        ('capture_objective', 'Capture Objective'),
        ('password_chain', 'Password Chain'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='tasks')
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Task zones
    zones = models.ManyToManyField(Zone, related_name='tasks')
    
    # Participants
    participating_players = models.ManyToManyField(Player, related_name='tasks', blank=True)
    progress = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Task metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['game', '-created_at']
    
    def __str__(self):
        return f"{self.type} task in {self.game.code} - {self.status}"


class Event(models.Model):
    """Game event log"""
    TYPE_CHOICES = [
        ('player_joined', 'Player Joined'),
        ('player_left', 'Player Left'),
        ('game_started', 'Game Started'),
        ('player_moved', 'Player Moved'),
        ('item_picked', 'Item Picked'),
        ('item_used', 'Item Used'),
        ('task_started', 'Task Started'),
        ('task_progress', 'Task Progress'),
        ('task_completed', 'Task Completed'),
        ('task_failed', 'Task Failed'),
        ('player_killed', 'Player Killed'),
        ('player_revived', 'Player Revived'),
        ('game_ended', 'Game Ended'),
        ('motion_detected', 'Motion Detected'),
        ('explosion', 'Explosion'),
        ('item_respawn', 'Item Respawn'),
    ]
    
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('team', 'Team'),
        ('private', 'Private'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='events')
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True, blank=True)
    
    # Event details
    message = models.TextField()
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='public')
    recipient_players = models.ManyToManyField(Player, related_name='private_events', blank=True)
    
    # Position (optional)
    position_lat = models.FloatField(null=True, blank=True)
    position_lng = models.FloatField(null=True, blank=True)
    
    # Additional data
    data = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['game', '-created_at']
    
    def __str__(self):
        return f"{self.type} in {self.game.code} at {self.created_at}"

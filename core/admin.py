from django.contrib import admin
from .models import (
    Game, Player, Zone, Event, ItemSpawn, 
    PlayerInventory, DeployedItem, StatusEffect, Task
)

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['code', 'status', 'host', 'created_at', 'started_at']
    list_filter = ['status', 'created_at']
    search_fields = ['code']
    readonly_fields = ['id', 'code', 'created_at', 'started_at', 'ended_at']

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['name', 'game', 'team', 'is_alive', 'is_online', 'visibility']
    list_filter = ['team', 'is_alive', 'is_online', 'visibility']
    search_fields = ['name', 'game__code']
    readonly_fields = ['id', 'joined_at', 'last_seen']

@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ['type', 'game', 'active', 'radius']
    list_filter = ['type', 'active']
    search_fields = ['game__code']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['type', 'game', 'player', 'visibility', 'created_at']
    list_filter = ['type', 'visibility', 'created_at']
    search_fields = ['game__code', 'player__name', 'message']
    readonly_fields = ['id', 'created_at']

@admin.register(ItemSpawn)
class ItemSpawnAdmin(admin.ModelAdmin):
    list_display = ['item_type', 'game', 'available', 'collected_by']
    list_filter = ['item_type', 'available']
    search_fields = ['game__code']

@admin.register(PlayerInventory)
class PlayerInventoryAdmin(admin.ModelAdmin):
    list_display = ['player', 'item', 'picked_up_at']
    search_fields = ['player__name']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['type', 'game', 'status', 'progress', 'created_at']
    list_filter = ['type', 'status']
    search_fields = ['game__code']

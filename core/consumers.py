import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Game, Player, Event
from .serializers import PlayerSerializer, EventSerializer


class GameConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time game updates"""
    
    async def connect(self):
        self.game_code = self.scope['url_route']['kwargs']['game_code']
        self.game_group_name = f'game_{self.game_code}'
        self.player_id = None
        
        # Join game group
        await self.channel_layer.group_add(
            self.game_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Mark player as offline if they were connected
        if self.player_id:
            await self.mark_player_offline(self.player_id)
            await self.channel_layer.group_send(
                self.game_group_name,
                {
                    'type': 'player_offline',
                    'player_id': str(self.player_id)
                }
            )
        
        # Leave game group
        await self.channel_layer.group_discard(
            self.game_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'authenticate':
                # Store player ID for this connection
                self.player_id = data.get('player_id')
                await self.mark_player_online(self.player_id)
                
                # Notify others that player is online
                await self.channel_layer.group_send(
                    self.game_group_name,
                    {
                        'type': 'player_online',
                        'player_id': str(self.player_id)
                    }
                )
            
            elif message_type == 'position_update':
                # Update player position
                await self.update_player_position(
                    self.player_id,
                    data.get('lat'),
                    data.get('lng'),
                    data.get('accuracy')
                )
                
                # Broadcast position to other players
                await self.channel_layer.group_send(
                    self.game_group_name,
                    {
                        'type': 'player_moved',
                        'player_id': str(self.player_id),
                        'position': {
                            'lat': data.get('lat'),
                            'lng': data.get('lng')
                        }
                    }
                )
            
            elif message_type == 'radar_ping':
                # Request positions of all visible players
                visible_players = await self.get_visible_players()
                await self.send(text_data=json.dumps({
                    'type': 'radar_response',
                    'players': visible_players
                }))
            
            elif message_type == 'chat':
                # Handle in-game chat (team or public)
                await self.handle_chat_message(
                    self.player_id,
                    data.get('message'),
                    data.get('visibility', 'public')
                )
            
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    # Message handlers for group broadcasts
    async def player_joined(self, event):
        """Handle player joined event"""
        await self.send(text_data=json.dumps({
            'type': 'player_joined',
            'player': event['player']
        }))
    
    async def player_left(self, event):
        """Handle player left event"""
        await self.send(text_data=json.dumps({
            'type': 'player_left',
            'player_id': event['player_id']
        }))
    
    async def player_online(self, event):
        """Handle player online event"""
        await self.send(text_data=json.dumps({
            'type': 'player_online',
            'player_id': event['player_id']
        }))
    
    async def player_offline(self, event):
        """Handle player offline event"""
        await self.send(text_data=json.dumps({
            'type': 'player_offline',
            'player_id': event['player_id']
        }))
    
    async def player_moved(self, event):
        """Handle player movement event"""
        # Don't send position updates back to the sender
        if event.get('player_id') != str(self.player_id):
            await self.send(text_data=json.dumps({
                'type': 'player_moved',
                'player_id': event['player_id'],
                'position': event['position']
            }))
    
    async def game_started(self, event):
        """Handle game start event"""
        await self.send(text_data=json.dumps({
            'type': 'game_started',
            'teams': event['teams']
        }))
    
    async def task_launched(self, event):
        """Handle task launch event"""
        await self.send(text_data=json.dumps({
            'type': 'task_launched',
            'task': event['task']
        }))
    
    async def task_updated(self, event):
        """Handle task update event"""
        await self.send(text_data=json.dumps({
            'type': 'task_updated',
            'task': event['task']
        }))
    
    async def item_collected(self, event):
        """Handle item collection event"""
        await self.send(text_data=json.dumps({
            'type': 'item_collected',
            'item_id': event['item_id'],
            'player_id': event['player_id']
        }))
    
    async def item_used(self, event):
        """Handle item use event"""
        await self.send(text_data=json.dumps({
            'type': 'item_used',
            'item_type': event['item_type'],
            'player_id': event['player_id'],
            'effects': event.get('effects', {})
        }))
    
    async def player_killed(self, event):
        """Handle player death event"""
        await self.send(text_data=json.dumps({
            'type': 'player_killed',
            'victim_id': event['victim_id'],
            'killer_id': event.get('killer_id'),
            'cause': event.get('cause')
        }))
    
    async def game_ended(self, event):
        """Handle game end event"""
        await self.send(text_data=json.dumps({
            'type': 'game_ended',
            'winner': event['winner'],
            'stats': event.get('stats', {})
        }))
    
    async def chat_message(self, event):
        """Handle chat message event"""
        # Check visibility rules
        if await self.should_receive_message(event):
            await self.send(text_data=json.dumps({
                'type': 'chat_message',
                'player_name': event['player_name'],
                'message': event['message'],
                'visibility': event['visibility'],
                'timestamp': event['timestamp']
            }))
    
    # Database operations
    @database_sync_to_async
    def mark_player_online(self, player_id):
        """Mark player as online"""
        try:
            player = Player.objects.get(id=player_id)
            player.is_online = True
            player.visibility = 'active'
            player.last_seen = timezone.now()
            player.save()
        except Player.DoesNotExist:
            pass
    
    @database_sync_to_async
    def mark_player_offline(self, player_id):
        """Mark player as offline"""
        try:
            player = Player.objects.get(id=player_id)
            player.is_online = False
            player.visibility = 'dark'
            player.save()
        except Player.DoesNotExist:
            pass
    
    @database_sync_to_async
    def update_player_position(self, player_id, lat, lng, accuracy=None):
        """Update player position in database"""
        try:
            player = Player.objects.get(id=player_id)
            player.position_lat = lat
            player.position_lng = lng
            if accuracy:
                player.position_accuracy = accuracy
            player.visibility = 'active'
            player.last_seen = timezone.now()
            player.save()
            
            # Log position event (throttle in production)
            Event.objects.create(
                game=player.game,
                type='player_moved',
                player=player,
                message=f"{player.name} moved",
                position_lat=lat,
                position_lng=lng,
                visibility='team'
            )
        except Player.DoesNotExist:
            pass
    
    @database_sync_to_async
    def get_visible_players(self):
        """Get list of visible players in the game"""
        try:
            game = Game.objects.get(code=self.game_code)
            players = game.players.filter(
                is_online=True,
                visibility__in=['active', 'recent']
            ).exclude(id=self.player_id)
            
            # Serialize player data
            return [
                {
                    'id': str(player.id),
                    'name': player.name,
                    'team': player.team,
                    'position': {
                        'lat': player.position_lat,
                        'lng': player.position_lng
                    } if player.position_lat else None,
                    'visibility': player.visibility
                }
                for player in players
            ]
        except Game.DoesNotExist:
            return []
    
    @database_sync_to_async
    def handle_chat_message(self, player_id, message, visibility):
        """Handle and broadcast chat message"""
        try:
            player = Player.objects.get(id=player_id)
            
            # Create chat event
            Event.objects.create(
                game=player.game,
                type='chat',
                player=player,
                message=message,
                visibility=visibility
            )
            
            # Broadcast to group
            return {
                'player_name': player.name,
                'player_team': player.team,
                'message': message,
                'visibility': visibility,
                'timestamp': timezone.now().isoformat()
            }
        except Player.DoesNotExist:
            return None
    
    @database_sync_to_async
    def should_receive_message(self, event):
        """Check if player should receive a message based on visibility"""
        if event['visibility'] == 'public':
            return True
        
        if not self.player_id:
            return False
        
        try:
            player = Player.objects.get(id=self.player_id)
            sender_team = event.get('player_team')
            
            if event['visibility'] == 'team':
                return player.team == sender_team
            
            if event['visibility'] == 'private':
                recipient_ids = event.get('recipient_ids', [])
                return str(self.player_id) in recipient_ids
            
        except Player.DoesNotExist:
            pass
        
        return False
# web/simple_consumers.py
"""
Simple WebSocket Consumer for Testing
Database integration for message persistence
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from datetime import datetime


class SimpleTestConsumer(AsyncWebsocketConsumer):
    """Simple WebSocket consumer for testing the bridge"""

    @database_sync_to_async
    def get_room(self, room_name):
        """Get or create room by name"""
        from server_websocket.models import Room
        room, created = Room.objects.get_or_create(
            slug=room_name,
            defaults={'name': room_name}
        )
        return room

    @database_sync_to_async
    def get_user(self, user_id):
        """Get user by ID"""
        from django.contrib.auth.models import User
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message(self, user, room, content):
        """Save message to database"""
        from server_websocket.models import Message
        return Message.objects.create(
            user=user,
            room=room,
            content=content
        )

    async def connect(self):
        print("Simple Consumer: Client connecting")
        
        # Get room name from URL
        url_route = self.scope.get('url_route', {})
        kwargs = url_route.get('kwargs', {})
        self.room_name = kwargs.get('room_slug')
        if not self.room_name:
            await self.close()
            print("Simple Consumer: No room_slug found in scope, closing connection.")
            return
        self.room_group_name = f"room_{self.room_name}"
        
        # Get user from scope
        self.user = self.scope.get('user')
        
        print(f"Simple Consumer: Connecting to room {self.room_name}")
        print(f"Simple Consumer: User from scope: {self.user}")
        print(f"Simple Consumer: User authenticated: {getattr(self.user, 'is_authenticated', False)}")
        print(f"Simple Consumer: User ID: {getattr(self.user, 'id', 'No ID')}")
        print(f"Simple Consumer: Username: {getattr(self.user, 'username', 'No username')}")
        
        # Get or create room
        self.room = await self.get_room(self.room_name)
        print(f"Simple Consumer: Room object: {self.room}")
        
        # Add to room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Add to broadcast group for REST API messages
        await self.channel_layer.group_add(
            "broadcast_group",
            self.channel_name
        )

        await self.accept()
        print(f"Simple Consumer: Client connected to room {self.room_name}")

        # Send welcome message
        await self.send(text_data=json.dumps({
            'type': 'connection_status',
            'status': 'connected',
            'room': self.room_name,
            'timestamp': datetime.now().isoformat(),
            'message': 'Welcome to the WebSocket connection!'
        }))

    async def disconnect(self, close_code):
        print(f"Simple Consumer: Client disconnected from room {self.room_name}")
        
        # Remove from groups
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        await self.channel_layer.group_discard(
            "broadcast_group",
            self.channel_name
        )

    async def receive(self, text_data):
        """Handle messages from WebSocket client"""
        try:
            data = json.loads(text_data)
            message_type = data.get('message_type', 'chat')  # Default to 'chat' if not specified
            
            print(f"Simple Consumer: Received {message_type} message: {data}")
            
            # Handle chat messages (both with and without message_type)
            if message_type == 'chat' or ('message' in data and 'username' in data):
                message_content = data.get('message', '').strip()
                username = data.get('username', 'Anonymous')
                
                print(f"Simple Consumer: Processing chat message: '{message_content}'")
                print(f"Simple Consumer: From username: '{username}'")
                print(f"Simple Consumer: Current user: {self.user}")
                print(f"Simple Consumer: User authenticated: {getattr(self.user, 'is_authenticated', False)}")
                
                # Only process non-empty messages
                if not message_content:
                    print("Simple Consumer: Empty message, skipping")
                    return
                
                # Save message to database if user is authenticated
                if self.user and self.user.is_authenticated:
                    try:
                        print(f"Simple Consumer: Attempting to save message to database...")
                        print(f"Simple Consumer: User: {self.user}")
                        print(f"Simple Consumer: Room: {self.room}")
                        
                        # Save message to database
                        saved_message = await self.save_message(
                            user=self.user,
                            room=self.room,
                            content=message_content
                        )
                        print(f"Simple Consumer: Message saved to database with PK {saved_message.pk}")
                        
                        # Use authenticated user's username
                        username = self.user.username
                        
                    except Exception as e:
                        print(f"Simple Consumer: Error saving message to database: {e}")
                        print(f"Simple Consumer: Exception type: {type(e)}")
                        import traceback
                        print(f"Simple Consumer: Traceback: {traceback.format_exc()}")
                        # Continue without saving to database
                else:
                    print(f"Simple Consumer: User not authenticated or None, not saving to database")
                    print(f"Simple Consumer: User: {self.user}")
                    print(f"Simple Consumer: User type: {type(self.user)}")
                
                # Echo back to the room
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message_content,
                        'username': username,
                        'timestamp': datetime.now().isoformat()
                    }
                )
            elif message_type == 'ping':
                # Respond to ping
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat(),
                    'original_message': data
                }))
            else:
                # Echo any other message type
                await self.send(text_data=json.dumps({
                    'type': 'echo',
                    'original_message': data,
                    'timestamp': datetime.now().isoformat()
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': 'Invalid JSON format',
                'timestamp': datetime.now().isoformat()
            }))
        except Exception as e:
            print(f"Simple Consumer: Error processing message: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': f'Error: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }))

    async def chat_message(self, event):
        """Send chat message to WebSocket"""
        # Handle both old format and new REST API format
        message_data = event.get('message', event.get('data', {}))
        
        if isinstance(message_data, dict):
            # New format from REST API
            await self.send(text_data=json.dumps({
                'type': 'api_message',
                'message': message_data,
                'timestamp': message_data.get('timestamp', datetime.now().isoformat()),
                'source': 'rest_api'
            }))
        else:
            # Old format from WebSocket chat
            await self.send(text_data=json.dumps({
                'type': 'chat_message',
                'message': event['message'],
                'username': event['username'],
                'timestamp': event['timestamp'],
                'source': 'websocket_chat'
            }))

    async def send_message_to_client(self, event):
        """Handle messages from REST API via websocket bridge"""
        message_type = event.get('message_type', 'api_message')
        data = event.get('data', {})
        
        await self.send(text_data=json.dumps({
            'type': message_type,
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'source': 'rest_api'
        }))
        
        print(f"Simple Consumer: Sent message from REST API: {message_type}")
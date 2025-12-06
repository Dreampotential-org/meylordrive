# server_agent/enhanced_consumers.py
"""
Enhanced WebSocket Consumers with REST API Bridge Support
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from datetime import datetime


class EnhancedServerAgentConsumer(AsyncWebsocketConsumer):
    """Enhanced Server Agent Consumer with REST API bridge support"""

    async def connect(self):
        print("ServerAgent: Client attempting connection")
        
        # Get API key from URL parameters
        api_key = self.scope.get('url_route', {}).get('kwargs', {}).get('api_key')
        
        # Authenticate user
        self.user = await self.authenticate_user(api_key)
        if self.user is None:
            print("ServerAgent: Authentication failed")
            await self.close()
            return

        # Store user in scope
        self.scope['user'] = self.user
        
        # Add to user-specific group for direct messaging
        await self.channel_layer.group_add(
            f"user_{self.user.username}",
            self.channel_name
        )
        
        # Add to agent-specific group if agent_id is provided
        self.agent_id = self.scope.get('url_route', {}).get('kwargs', {}).get('agent_id')
        if self.agent_id:
            await self.channel_layer.group_add(
                f"agent_{self.agent_id}",
                self.channel_name
            )
            print(f"ServerAgent: Agent {self.agent_id} connected")
        
        # Add to broadcast group for global messages
        await self.channel_layer.group_add(
            "broadcast_group",
            self.channel_name
        )

        await self.accept()
        print(f"ServerAgent: User {self.user.username} connected successfully")
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_status',
            'status': 'connected',
            'user': self.user.username,
            'agent_id': self.agent_id,
            'timestamp': datetime.now().isoformat()
        }))

    async def disconnect(self, close_code):
        print(f"ServerAgent: User {getattr(self, 'user', 'Unknown')} disconnected with code {close_code}")
        
        # Remove from all groups
        if hasattr(self, 'user') and self.user:
            await self.channel_layer.group_discard(
                f"user_{self.user.username}",
                self.channel_name
            )
        
        if hasattr(self, 'agent_id') and self.agent_id:
            await self.channel_layer.group_discard(
                f"agent_{self.agent_id}",
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
            message_type = data.get('type', 'unknown')
            
            print(f"ServerAgent: Received {message_type} from {self.user.username}")
            
            if message_type == 'ping':
                await self.handle_ping(data)
            elif message_type == 'agent_status':
                await self.handle_agent_status(data)
            elif message_type == 'command_response':
                await self.handle_command_response(data)
            else:
                await self.handle_generic_message(data)
                
        except json.JSONDecodeError:
            print("ServerAgent: Invalid JSON received")
            await self.send_error("Invalid JSON format")
        except Exception as e:
            print(f"ServerAgent: Error processing message: {e}")
            await self.send_error(f"Error processing message: {str(e)}")

    async def handle_ping(self, data):
        """Handle ping messages"""
        await self.send(text_data=json.dumps({
            'type': 'pong',
            'timestamp': datetime.now().isoformat(),
            'original_data': data
        }))

    async def handle_agent_status(self, data):
        """Handle agent status updates"""
        # You can store this in database or forward to other systems
        print(f"Agent {self.agent_id} status: {data}")
        
        # Echo back confirmation
        await self.send(text_data=json.dumps({
            'type': 'status_received',
            'agent_id': self.agent_id,
            'status': data.get('status'),
            'timestamp': datetime.now().isoformat()
        }))

    async def handle_command_response(self, data):
        """Handle responses from executed commands"""
        print(f"Command response from agent {self.agent_id}: {data}")
        
        # You can process the response or forward it to other services
        await self.send(text_data=json.dumps({
            'type': 'response_received',
            'command_id': data.get('command_id'),
            'success': data.get('success', True),
            'timestamp': datetime.now().isoformat()
        }))

    async def handle_generic_message(self, data):
        """Handle other message types"""
        await self.send(text_data=json.dumps({
            'type': 'message_received',
            'original_type': data.get('type'),
            'processed': True,
            'timestamp': datetime.now().isoformat()
        }))

    # Methods called from REST API via channel layer
    async def send_message_to_client(self, event):
        """Send message to client (called from REST API via websocket_bridge)"""
        message_type = event.get('message_type')
        data = event.get('data')
        
        await self.send(text_data=json.dumps({
            'type': message_type,
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'source': 'rest_api'
        }))

    async def send_agent_command(self, event):
        """Send command to agent (called from REST API via websocket_bridge)"""
        command_data = event.get('command_data')
        
        await self.send(text_data=json.dumps({
            'type': 'agent_command',
            'command': command_data.get('command'),
            'data': command_data.get('data'),
            'agent_id': command_data.get('agent_id'),
            'timestamp': datetime.now().isoformat(),
            'source': 'rest_api'
        }))

    async def send_error(self, error_message):
        """Send error message to client"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'error': error_message,
            'timestamp': datetime.now().isoformat()
        }))

    @database_sync_to_async
    def authenticate_user(self, api_key):
        """Authenticate user based on API key"""
        try:
            # Try to find user by API key - you might need to adjust this
            # based on your User model structure
            if hasattr(User, 'api_key'):
                user = User.objects.get(api_key=api_key)
            else:
                # Fallback: create a simple authentication mechanism
                # You should implement proper API key authentication
                user = User.objects.filter(is_staff=True).first()
                if not user:
                    return None
            return user
        except User.DoesNotExist:
            return None
        except Exception as e:
            print(f"Authentication error: {e}")
            return None


class EnhancedChatConsumer(AsyncWebsocketConsumer):
    """Enhanced Chat Consumer with REST API bridge support"""

    async def connect(self):
        print("ChatConsumer: Client connecting")
        
        # Get room name from URL
        self.room_name = self.scope['url_route']['kwargs']['room_slug']
        self.room_group_name = f"room_{self.room_name}"
        
        # Get user from scope
        self.user = self.scope.get('user')
        
        # Add to room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Add to user group if authenticated
        if self.user and not self.user.is_anonymous:
            await self.channel_layer.group_add(
                f"user_{self.user.username}",
                self.channel_name
            )
        
        # Add to broadcast group
        await self.channel_layer.group_add(
            "broadcast_group",
            self.channel_name
        )

        await self.accept()
        print(f"ChatConsumer: Client connected to room {self.room_name}")

    async def disconnect(self, close_code):
        print(f"ChatConsumer: Client disconnected from room {self.room_name}")
        
        # Remove from all groups
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        if self.user and not self.user.is_anonymous:
            await self.channel_layer.group_discard(
                f"user_{self.user.username}",
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
            message_type = data.get('message_type', 'chat')
            
            if message_type == 'chat':
                await self.handle_chat_message(data)
            elif message_type == 'health_status':
                await self.handle_health_status(data)
            else:
                await self.handle_generic_message(data)
                
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON format")
        except Exception as e:
            print(f"ChatConsumer: Error processing message: {e}")
            await self.send_error(f"Error: {str(e)}")

    async def handle_chat_message(self, data):
        """Handle chat messages"""
        message = data.get('message', '')
        username = data.get('username', 'Anonymous')
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'timestamp': datetime.now().isoformat()
            }
        )

    async def handle_health_status(self, data):
        """Handle health status messages"""
        # Process health status data
        print(f"Health status received: {data}")
        
        # You can save to database or forward to other services here
        
        # Send acknowledgment
        await self.send(text_data=json.dumps({
            'type': 'health_status_received',
            'status': 'processed',
            'timestamp': datetime.now().isoformat()
        }))

    async def handle_generic_message(self, data):
        """Handle other message types"""
        await self.send(text_data=json.dumps({
            'type': 'message_processed',
            'original_data': data,
            'timestamp': datetime.now().isoformat()
        }))

    # Message handlers called from channel layer
    async def chat_message(self, event):
        """Send chat message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'username': event['username'],
            'timestamp': event['timestamp']
        }))

    async def send_message_to_client(self, event):
        """Send message to client (called from REST API)"""
        message_type = event.get('message_type')
        data = event.get('data')
        
        await self.send(text_data=json.dumps({
            'type': message_type,
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'source': 'rest_api'
        }))

    async def send_error(self, error_message):
        """Send error message to client"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'error': error_message,
            'timestamp': datetime.now().isoformat()
        }))
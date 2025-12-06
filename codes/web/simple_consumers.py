# web/simple_consumers.py
"""
Simple WebSocket Consumer for Testing
No dependencies on external models
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime


class SimpleTestConsumer(AsyncWebsocketConsumer):
    """Simple WebSocket consumer for testing the bridge"""

    async def connect(self):
        print("Simple Consumer: Client connecting")
        
        # Get room name from URL
        self.room_name = self.scope['url_route']['kwargs']['room_slug']
        self.room_group_name = f"room_{self.room_name}"
        
        print(f"Simple Consumer: Connecting to room {self.room_name}")
        
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
            message_type = data.get('message_type', 'chat')
            
            print(f"Simple Consumer: Received {message_type} message")
            
            if message_type == 'chat':
                message = data.get('message', '')
                username = data.get('username', 'Anonymous')
                
                # Echo back to the room
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
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
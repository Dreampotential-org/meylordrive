# server_agent/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User  # Import User model if used
# from agent.models import ApiKey  
# from django.contrib.auth.models import User
# from agent.models import ApiKey
from channels.db import database_sync_to_async

from server_agent.models import CustomUser

class ServerAgentConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # Authenticate user from API key
        print("Hello a client has connected")
        api_key = self.scope.get(
            'url_route', {}).get('kwargs', {}).get('api_key')
        user = await self.authenticate_user(api_key)
        if user is None:
            await self.close()
            return

        # Add user to a group (if needed)
        # You can use groups for different purposes like broadcasting messages
        await self.channel_layer.group_add(
            # You can use the user's username or any unique identifier
            user.username,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        print("User disconnected with code %s" % close_code)
        # Remove user from the group
        user = self.scope.get('user')
        if user:
            await self.channel_layer.group_discard(
                user.username, self.channel_name
            )

    async def receive(self, text_data):
        print("Got an incoming messagge %s" % text_data)
        # Handle incoming WebSocket messages
        user = self.scope.get('user')
        if user:
            # Process the message, e.g., run a command on the client.py
            # You can define the logic here based on your requirements
            await self.send(text_data=json.dumps({
                'message': 'Command executed successfully',
            }))

    @database_sync_to_async
    def authenticate_user(self, api_key):
        try:
            user = CustomUser.objects.get(api_key=api_key)
            self.scope['user'] = user
            return user
        except CustomUser.DoesNotExist as e:
            print(f"User with api_key={api_key} does not exist. Error: {e}")
            return None
        except Exception as e:
            print(f"Error during user authentication: {e}")
            return None
  # Import ApiKey model


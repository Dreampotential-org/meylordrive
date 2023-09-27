# server_agent/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ServerAgentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Authenticate user from API key
        api_key = self.scope.get('url_route', {}).get('kwargs', {}).get('api_key')
        user = await self.authenticate_user(api_key)
        if user is None:
            await self.close()
            return

        # Add user to a group (if needed)
        # You can use groups for different purposes like broadcasting messages
        await self.channel_layer.group_add(
            user.username,  # You can use the user's username or any unique identifier
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Remove user from the group
        user = self.scope.get('user')
        if user:
            await self.channel_layer.group_discard(
                user.username, self.channel_name
            )

    async def receive(self, text_data):
        # Handle incoming WebSocket messages
        user = self.scope.get('user')
        if user:
            # Process the message, e.g., run a command on the client.py
            # You can define the logic here based on your requirements
            await self.send(text_data=json.dumps({
                'message': 'Command executed successfully',
            }))

    async def authenticate_user(self, api_key):
        # Implement your authentication logic here
        # Return the authenticated user or None if authentication fails
        try:
            user = User.objects.get(api_key=api_key)
            self.scope['user'] = user
            return user
        except User.DoesNotExist:
            return None

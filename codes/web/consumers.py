import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone  # Import 'timezone' from 'django.utils'
from server_websocket.models import WebSocketConnection
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "group_chat_gfg"

        # Save information about the WebSocket connection
        connection_info = WebSocketConnection.objects.create(
            room_group=self.room_group_name,
            connection_time=timezone.now()
        )

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Log the WebSocket connection establishment
        print(f"WebSocket Connection established in room {self.room_group_name} at {connection_info.connection_time}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json["message"]
            username = text_data_json["username"]
        except KeyError as e:
            print(f"Received data does not contain key: {e}")
            return

        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "send_message",
                "message": message,
                "username": username,
            })

    async def send_message(self, event):
        message = event["message"]
        username = event["username"]

        # Log the message being sent
        print(f"Message sent to room {self.room_group_name} - User: {username}, Message: {message}")

        await self.send(text_data=json.dumps({"message": message, "username": username}))
class CreateRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "group_create_room"
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            room_name = text_data_json["room_name"]
        except KeyError as e:
            print(f"Received data does not contain key: {e}")
            return

        # Create room logic here, e.g., save to the database
        # Emit a message to the group with the new room information
        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "send_message",
                "room_name": room_name,
            })

    async def send_message(self, event):
        room_name = event["room_name"]
        await self.send(text_data=json.dumps({"room_name": room_name}))
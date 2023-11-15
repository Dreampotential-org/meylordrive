import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom

class ChatRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"

        await self.accept()

    async def disconnect(self, close_code):
        print(f"Disconnecting {self.channel_name} from {self.room_group_name}")
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        if message['type'] == 'create_room':
            await self.create_room(message)
        else:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat.message',
                    'message': message
                }
            )

    async def chat_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def create_room(self, message):
        room_name = message.get('room_name')
        if room_name:
            # Check if the room already exists
            room_exists = await database_sync_to_async(ChatRoom.objects.filter(name=room_name).exists)()

            if not room_exists:
                # Create the room in the database
                new_room = await database_sync_to_async(ChatRoom.objects.create)(name=room_name)

                # Broadcast the new room to all connected clients in the lobby
                await self.channel_layer.group_add(
                    'chat_lobby',
                    self.channel_name
                )

                await self.channel_layer.group_send(
                    'chat_lobby',
                    {
                        'type': 'list_rooms',
                        'message': f'Room {room_name} created successfully!'
                    }
                )
            else:
                await self.send(text_data=json.dumps({
                    'message': f'Room {room_name} already exists.'
                }))
        else:
            await self.send(text_data=json.dumps({
                'message': 'Invalid room name provided for creation.'
            }))

    async def list_rooms(self):
        # Get the list of existing rooms from the database
        rooms = await database_sync_to_async(ChatRoom.objects.values_list('name', flat=True))()

        # Send the list of rooms to the connected client
        await self.send(text_data=json.dumps({
            'message': 'Available Rooms: ' + ', '.join(rooms)
        }))



    async def join_room(self, message):
        room_name = message['room_name']

        # Add logic to check if the room exists before joining
        if await database_sync_to_async(ChatRoom.objects.filter(name=room_name).exists)():
            await self.channel_layer.group_add(
                room_name,
                self.channel_name
            )

            # Inform the client that they have successfully joined the room
            await self.send(text_data=json.dumps({
                'message': f'You have joined the room: {room_name}'
            }))
        else:
            # Inform the client that the room does not exist
            await self.send(text_data=json.dumps({
                'message': f'The room {room_name} does not exist.'
            }))

    async def leave_room(self, message):
        room_name = message['room_name']

        # Remove the consumer from the room group
        await self.channel_layer.group_discard(
            room_name,
            self.channel_name
        )

        # Inform the client that they have successfully left the room
        await self.send(text_data=json.dumps({
            'message': f'You have left the room: {room_name}'
        }))

    async def get_room_info(self, message):
        room_name = message['room_name']

        # Add logic to retrieve room information from the database
        room = await database_sync_to_async(ChatRoom.objects.filter(name=room_name).first)()

        if room:
            # Inform the client with the room information
            await self.send(text_data=json.dumps({
                'message': f'Room Info: {room_name}',
                'info': {
                    'name': room.name,
                    'created_at': room.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    # Add more fields as needed
                }
            }))
        else:
            # Inform the client that the room does not exist
            await self.send(text_data=json.dumps({
                'message': f'The room {room_name} does not exist.'
            }))


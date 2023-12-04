import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from datetime import datetime, timedelta, timezone as tz
from django.utils import timezone
import pytz

from server_websocket.models import Room, Message, User, UserRoomActivity
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from utils.chirp import CHIRP


from tasks.models import StatsEntry


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_slug']
        self.room_group_name = 'chat_%s' % self.room_name
        self.user = self.scope['user']
        self.entry_time = datetime.now()
        print(f"User {self.user} connected to room {self.room_name} at {self.entry_time}")

        # Add the user to the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Save user activity entry time
        print(self.user)
        if str(self.user) != "AnonymousUser":
            await self.save_user_activity(entry=True)

        await self.accept()

    async def disconnect(self, close_code):
        # Remove the user from the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Save user activity exit time
        if str(self.user) != "AnonymousUser":
            await self.save_user_activity(entry=False)
            ist_exit_time = datetime.now(tz.utc).astimezone(
                tz(timedelta(hours=5, minutes=30))
            )  # Convert to IST
            print(f"User {self.user} disconnected from room {self.room_name} at {ist_exit_time}")

    async def receive(self, text_data):
        CHIRP.info("We recieved message: %s" % text_data)
        data_json = json.loads(text_data)
        message_type = data_json["message_type"]
        if message_type == 'health_status':
            await self.save_stats_entry(data_json['message'])
        else:
            message = data_json["message"]
            username = data_json["username"]
            room_name = data_json["room_name"]

            # Save the message
            await self.save_message(message, username, room_name)

            # Send the message to the room group
            await self.channel_layer.group_send(
                self.room_group_name, {
                    "type": "send_message",
                    "message": message,
                    "username": username,
                    "room_name": room_name,
                }
            )

    async def send_message(self, event):
        message = event["message"]
        username = event["username"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "message": message,
            "username": username,
        }))

    # @database_sync_to_async
    async def get_or_create_user_activity(self, user, room):
        user_activities = await database_sync_to_async(UserRoomActivity.objects.filter)(
            user=user,
            room=room,
            exit_time__isnull=True
        )

        if await database_sync_to_async(user_activities.exists)():
            user_activity = await database_sync_to_async(user_activities.get)()
            return user_activity, False
        else:
            user_activity, created = await database_sync_to_async(
                UserRoomActivity.objects.get_or_create)(
                    user=user,
                    room=room,
                    exit_time__isnull=True
                )
            return user_activity, created

    @database_sync_to_async
    def get_room(self, room_name):
        try:
            return Room.objects.get(slug=room_name)
        except Room.DoesNotExist:
            # Handle the case when the room does not exist
            raise Exception(f"Room {room_name} does not exist")

    async def save_user_activity(self, entry=False):
        room_name = self.room_name
        room = await self.get_room(room_name)

        if not room:
            return

        try:
            if entry:
                user_activity, created = await self.get_or_create_user_activity(self.user, room)
                user_activity.entry_time = timezone.now()
            else:
                user_activity = await database_sync_to_async(UserRoomActivity.objects.get)(
                    user=self.user,
                    room=room,
                    exit_time__isnull=True
                )
                user_activity.exit_time = datetime.now(tz=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata'))  # Convert to IST

                # Calculate and save duration
                if user_activity.entry_time and user_activity.exit_time:
                    duration = user_activity.exit_time - user_activity.entry_time
                    user_activity.duration = duration.total_seconds()

            if user_activity:
                await database_sync_to_async(user_activity.save)()

        except ObjectDoesNotExist:
            # Handle the case where the activity does not exist
            print("UserRoomActivity does not exist.")

    @sync_to_async
    def save_message(self, message, username, room_name):
        user = User.objects.get(username=username)

        # Get or create the room
        room, created = Room.objects.get_or_create(slug=room_name, defaults={'name': room_name})
        Message.objects.create(user=user, room=room, content=message)

    @sync_to_async
    def save_message(self, message, username, room_name):
        user = User.objects.get(username=username)

        # Get or create the room
        room, created = Room.objects.get_or_create(
            slug=room_name, defaults={'name': room_name})
        Message.objects.create(user=user, room=room, content=message)

    @sync_to_async
    def save_stats_entry(self, stats_json):
        CHIRP.info("Save sats entry: %s" % stats_json)
        return StatsEntry.objects.create(
            system=stats_json['System'],
            node_name=stats_json['Node Name'],
            release=stats_json['Release'],
            version=stats_json['Version'],
            machine=stats_json['Machine'],
            processor=stats_json['Processor'],
            ip_address=stats_json['Ip-Address'],
            mac_address=','.join(stats_json['Mac-Address']),
            total_swap=stats_json['TotalSwap'],
            swap_free=stats_json['SwapFree'],
            used_swap=stats_json['UsedSwap'],
            swap_percentage=stats_json['SwapPercentage'],
            total_bytes_sent=stats_json['TotalBytesSent'],
            total_bytes_received=stats_json['TotalBytesReceived'],
            # total_read=stats_json['TotalRead'],
            # total_write=stats_json['TotalWrite'],
        )


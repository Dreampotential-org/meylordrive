import json
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from datetime import datetime, timedelta, timezone as tz
from django.utils import timezone
import pytz
from drive.models import Contact

from server_websocket.models import Room, Message, User, UserRoomActivity
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from utils.chirp import CHIRP

from tasks.models import StatsEntry, Agent
from drive.management.commands.google_voice_outbound import init_driver, google_utils




class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        query_string = self.scope["query_string"].decode("utf-8")
        if "&agent_id=" in query_string:
            self.agent_id = query_string.split("&agent_id=")[1]
            print(self.agent_id)
            await self.set_agent_active(self.agent_id)
        else:
            self.agent_id = None  # Set a default value or handle the absence of agent_id

        try:
            # Try to get 'room_slug' from the URL route parameters
            self.room_name = self.scope['url_route']['kwargs']['room_slug']
        except KeyError:
            # Handle the absence of 'room_slug' (set a default or log a warning)
            self.room_name = 'contact'
            # Log a warning or provide a default value based on your requirements
            print("Warning: 'room_slug' not found in URL route. Using default room name.")

        self.room_group_name = self.room_name
        self.user = self.scope['user']
        self.entry_time = datetime.now()
        print(f"User {self.user} connected to room {self.room_name} at {self.entry_time}")

        # Add the user to the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Save user activity entry time
        if str(self.user) != "AnonymousUser":
            await self.save_user_activity(entry=True)

        # Retrieve contact details dynamically based on the user or room information
        # You can replace the following line with your dynamic logic to get contact_id
        contact_id = 232  
        try:
            contact = Contact.objects.get(pk=contact_id)
            contact_name = contact.name
            contact_phone = contact.phone_number

            # Print the contact details
            print(f"Contact ID: {contact_id}")
            print(f"Contact Name: {contact_name}")
            print(f"Contact Phone Number: {contact_phone}")


        # Send the message to the room group
            # await self.channel_layer.group_send(
            #     self.room_group_name, {  
            #     'message_type': 'outbound_call',
            #     'contact_id': contact_id,
            # })





        except Contact.DoesNotExist:
            print(f"Contact with ID {contact_id} does not exist.")

        await self.accept()
        # await self.save_message(message, username, room_name)


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

        if self.agent_id:
            await self.set_agent_not_active(self.agent_id)

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
        try:
            message = event["message"]
            username = event["username"]

            # Send message to WebSocket
            await self.send(text_data=json.dumps({
                "message": message,
                "username": username,
            }))
            print(f"Message sent successfully: {message} from {username}")
        except Exception as e:
            print(f"Error in send_message function: {e}")


    # @database_sync_to_async
    async def get_or_create_user_activity(self, user, room):
        user_activities = await database_sync_to_async(
                UserRoomActivity.objects.filter
        )(
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
                user_activity, created = await self.get_or_create_user_activity(
                    self.user, room)
                user_activity.entry_time = timezone.now()
            else:
                user_activity = await database_sync_to_async(
                    UserRoomActivity.objects.get)(
                        user=self.user,
                        room=room,
                        exit_time__isnull=True
                    )
                user_activity.exit_time = datetime.now(tz=pytz.utc).astimezone(
                    pytz.timezone('Asia/Kolkata'))  # Convert to IST

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
        room, created = Room.objects.get_or_create(
            slug=room_name, defaults={'name': room_name})
        Message.objects.create(user=user, room=room, content=message)

    # @sync_to_async
    # def save_message(self, message, username, room_name):
    #     user = User.objects.get(username=username)

    #     # Get or create the room
    #     room, created = Room.objects.get_or_create(
    #         slug=room_name, defaults={'name': room_name})
    #     Message.objects.create(user=user, room=room, content=message)


    @sync_to_async
    def set_agent_active(self, agent_id):
        agent = Agent.objects.filter(id=agent_id).first()
        if not agent:
            agent = Agent()
            agent.id = agent_id
        agent.alive = True
        agent.save()

    @sync_to_async
    def set_agent_not_active(self, agent_id):
        agent = Agent.objects.filter(id=agent_id).first()
        if not agent:
            agent = Agent()
            agent.id = agent_id
        
        agent.alive = False
        agent.save()


    @sync_to_async
    def save_stats_entry(self, stats_json):
        agent_id = stats_json.pop('agent_id')
        agent = Agent.objects.filter(id=agent_id).first()
        if not Agent:
            agent = Agent()
            agent.id = agent_id
            agent.save()

        CHIRP.info("Save entry: %s" % stats_json)
        return StatsEntry.objects.create(
            agent=agent,
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
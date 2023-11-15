# server_websocket/consumers.py
import datetime
from gettext import translation
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from utils.chirp import CHIRP
from tasks.models import StatsEntry, ApiKey, Agent
from asgiref.sync import sync_to_async
from django.db import transaction

import django
django.setup()
class ChatConsumer(AsyncWebsocketConsumer):
    """
    A consumer 
    that handles WebSocket connections for chat functionality.
            """
    async def authenticate_user(self, api_key):
        print("HERE is the api key from the agentwoot! %s" % api_key)

        # Retrieve the ApiKey instance
        api_key_instance = ApiKey.objects.filter(key=str(api_key)).first()

        # Check if the ApiKey exists
        if api_key_instance is None:
            # Send an error message and close the connection
            await self.send(text_data=json.dumps({'error': 'Invalid API key'}))
            await self.close()  # Close the connection
            return None

        # Create a new Agent instance and set the api_key_id
        agent = Agent(api_key=api_key_instance)
        agent.alive = True
        agent.save()
        return api_key_instance

    async def connect(self):
        self.room_name = None
        room_name_param = self.scope['url_route'].get('kwargs', {}).get('room_name')

        if room_name_param:
            self.room_name = room_name_param
            self.room_group_name = f"chat_{self.room_name}"

            api_key = self.scope["query_string"].decode("utf-8").split("api_key=")[1]
            api_key_obj = await self.authenticate_user(api_key)

            if api_key_obj:
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
                await self.accept()
        else:
            # Handle the case where 'room_name' is not present in the URL
            await self.close(code=4000)

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        print("We got something new... %s" % text_data)
        # Decoding the received JSON text data
        stats_json = json.loads(text_data)
        # Calling create_entry async function to create a new entry
        # in the database with the received data
        new_entry = await self.save_stats_entry(stats_json)
        CHIRP.info("New entry created: %s" % new_entry)
        # Uncomment the next line if you want to print
        # the newly created entry's data
        # await self.print_stats_data(new_entry)

        # XXX Make it more obvious how this api is working
        # /get_task

        # XXX how to fetch Server stats-agent is active on
        await self.send_task_data()

    async def send_task_data(self):
        # Call the sync function to get project command in async context
        project_command = await database_sync_to_async(
            self.get_project_command
        )()

        # Check if a project_command is found
        if project_command:
            print(f"Project Command: {project_command}")
            await self.send(json.dumps(project_command))
        else:
            # If no project_command is found, you can send a message
            # to indicate that the queue is empty
            await self.send(json.dumps({'message': 'No tasks available.'}))

    # Define synchronous method for getting project command
    def get_project_command(self):
        from tasks.models import ProjectCommand  # Move import here
        with transaction.atomic():

            project_command = ProjectCommand.objects.select_for_update(
                skip_locked=True
            ).filter().exclude(status__isnull=False).first()

            if project_command:
                # XXX We need some way to handle status when is not running
                # or in error state
                project_command.status = 'running'
                project_command.save()
        return project_command

    # Decorating the function to be run in a synchronous manner
    @database_sync_to_async
    def save_stats_entry(self, stats_json):
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

    @staticmethod
    async def print_stats_data(entry):
        from tasks.models import StatsEntry  # Move import here
        stats_data = await database_sync_to_async(
            ChatConsumer.get_fields
        )(entry)
        print(stats_data)

    @staticmethod
    def get_fields(entry):
        # XXX Expand to take more snapshot of node and processing table
        return {
            'system': entry.system,
            'node_name': entry.node_name,
            'release': entry.release,
            'version': entry.version,
            'machine': entry.machine,
            'processor': entry.processor,
            'ip_address': entry.ip_address,
            'mac_address': entry.mac_address,
            'total_swap': entry.total_swap,
            'swap_free': entry.swap_free,
            'used_swap': entry.used_swap,
            'swap_percentage': entry.swap_percentage,
            'total_bytes_sent': entry.total_bytes_sent,
            'total_bytes_received': entry.total_bytes_received,
            'total_read': entry.total_read,
            'total_write': entry.total_write,
        }

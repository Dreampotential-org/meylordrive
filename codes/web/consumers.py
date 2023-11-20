# server_websocket/consumers.py
import json
import datetime
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from django.db import transaction
from django.contrib.auth.models import User
from server_websocket.models import ProjectCommand, Room, Message, StatsEntry, ApiKey, Agent
from tasks.models import ProjectCommand
from utils.chirp import CHIRP

class ChatConsumer(AsyncWebsocketConsumer):
    async def authenticate_user(self, api_key):
        api_key_instance = ApiKey.objects.filter(key=str(api_key)).first()
        if api_key_instance is None:
            await self.send(text_data=json.dumps({'error': 'Invalid API key'}))
            await self.close()
            return None

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
            await self.close(code=4000)

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        stats_json = json.loads(text_data)
        new_entry = await self.save_stats_entry(stats_json)
        CHIRP.info("New entry created: %s" % new_entry)
        await self.send_task_data()

    async def send_task_data(self):
        project_command = await database_sync_to_async(
            self.get_project_command
        )()

        if project_command:
            await self.send(json.dumps(project_command))
        else:
            await self.send(json.dumps({'message': 'No tasks available.'}))

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
        )

    def get_project_command(self):
        with transaction.atomic():
            project_command = ProjectCommand.objects.select_for_update(
                skip_locked=True
            ).filter().exclude(status__isnull=False).first()

            if project_command:
                project_command.status = 'running'
                project_command.save()
        return project_command

    @staticmethod
    async def print_stats_data(entry):
        stats_data = await database_sync_to_async(
            ChatConsumer.get_fields
        )(entry)
        print(stats_data)

    @staticmethod
    def get_fields(entry):
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
        }

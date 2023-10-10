# chat_app/consumers.py
import datetime
import json
from channels.generic.websocket import AsyncWebsocketConsumer
# from tasks.models import StatsEntry
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    """
    A consumer that handles WebSocket connections for chat functionality.
    """
    async def connect(self):
        """
        Async function called when the WebSocket is handshaking as part of connection process.
        """
        await self.accept()

    async def disconnect(self, close_code):
        """
        Async function called when the WebSocket closes for any reason.
        :param close_code: Provides the reason the WebSocket closed.
        """
        pass

    async def receive(self, text_data):
        """
        Async function called when the server receives a message from WebSocket.
        :param text_data: Text data received from the WebSocket.
        """
        stats_json = json.loads(text_data)  # Decoding the received JSON text data
        # Calling create_entry async function to create a new entry in the database with the received data
        new_entry = await self.create_entry(stats_json)
        # Uncomment the next line if you want to print the newly created entry's data
        # await self.print_stats_data(new_entry)

    @database_sync_to_async  # Decorating the function to be run in a synchronous manner
    def get_task(self, req_params):

        # get a task on a node...
        # XXX we will need to do like mark the task being running on server.

        with transaction.atomic():
            project_command = ProjectCommand.objects.select_for_update(
                    skip_locked=True).filter(
                ).exclude(status='running').first()

            if project_command:
                project_command.status = 'running'
                project_command.save()


            # do some clean up method
            # last_heard_running


            # update status
            # project_commands[0].status == 'running'

        return project_commands[0]


    @database_sync_to_async  # Decorating the function to be run in a synchronous manner
    def create_entry(self, stats_json):
        """
        Synchronous function to create a new entry in the database with the provided JSON data.
        Decorated with @database_sync_to_async to be called from async contexts.
        :param stats_json: The JSON data used to create a new entry.
        :return: The newly created entry.
        """
        from tasks.models import StatsEntry
        # Creating and returning a new StatsEntry with the data provided in stats_json
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
        """
        Async static method to print the data of the provided entry.
        :param entry: The entry whose data is to be printed.
        """
        # Retrieving and printing the fields of the provided entry using the get_fields static method
        stats_data = await database_sync_to_async(ChatConsumer.get_fields)(entry)
        print(stats_data)

    @staticmethod
    def get_fields(entry):
        """
        Static method to retrieve and return the fields of the provided entry as a dictionary.
        :param entry: The entry whose fields are to be retrieved.
        :return: A dictionary containing the fields of the entry.
        """
        # Creating and returning a dictionary with the fields and values of the provided entry
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

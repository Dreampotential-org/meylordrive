# drive/management/commands/websocket_task.py

import asyncio
import websockets
from django.core.management.base import BaseCommand
from drive.models import Contact

class Command(BaseCommand):
    help = 'Perform a task involving WebSocket and Contact model'

    async def send_websocket_message(self):
        uri = "wss://agentstat.com?contract=1"
        async with websockets.connect(uri) as websocket:
            message = "YourWebSocketMessageHere"
            await websocket.send(message)
            response = await websocket.recv()
            self.stdout.write(self.style.SUCCESS(f"Received response from WebSocket server: {response}"))

    def print_contact_details(self):
        # Assuming 'Contact' is the model class in drive.models
        contact_id = 1
        try:
            contact = Contact.objects.get(pk=contact_id)
            self.stdout.write(self.style.SUCCESS(
                f"Contact ID: {contact.id}, Name: {contact.name}, Email: {contact.email}")
            )
        except Contact.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Contact with ID {contact_id} does not exist."))

    async def handle(self, *args, **options):
        # First, send a message to the WebSocket server
        await self.send_websocket_message()

        # Then, print details of Contact with ID 1
        self.print_contact_details()

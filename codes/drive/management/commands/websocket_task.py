import asyncio
import sys
from django.core.management import execute_from_command_line
from django.core.management.base import BaseCommand
from drive.models import Contact

class Command(BaseCommand):
    help = 'Your command description here'

    async def send_websocket_message(self):
        uri = "ws://agentstat.com?contract=1"
        # Your WebSocket message sending logic here

    def print_contact_details(self):
        contact_id = 1
        try:
            contact = Contact.objects.get(pk=contact_id, phone_number__isnull=False)
            self.stdout.write(self.style.SUCCESS(f"Contact ID: {contact.id}, Phone: {contact.phone_number}"))
        except Contact.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Contact with ID {contact_id} does not exist."))

    async def run_task(self):
        # First, send a message to the WebSocket server
        await self.send_websocket_message()

        self.print_contact_details()

    def handle(self, *args, **options):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.run_task())
        loop.close()

if __name__ == '__main__':
    execute_from_command_line(sys.argv)

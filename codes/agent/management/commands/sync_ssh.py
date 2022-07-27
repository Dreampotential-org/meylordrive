from tasks.models import Task, Server, SystemSpecs, TaskLog, ServerUserKey
import os
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'run the tasks'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        print("Start...")

        # at the start we clear all severs that are in use.
        servers = Server.objects.filter().exclude(system_specs=None)
        for server in servers:
            server_user_keys = ServerUserKey.objects.filter(server=server)
            authorized_keys = ""
            for server_user_key in server_user_keys:
                authorized_keys += server_user_key.keypair
            print(authorized_keys)

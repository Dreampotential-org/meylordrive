from tasks.models import Task, Server, ServerUserKey, KeyPair
import os
from django.core.management.base import BaseCommand
from agent.management.commands.run_tasks import configure_node


class Command(BaseCommand):
    help = 'run the tasks'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        print("Start...")

        # get a list of servers
        servers = Server.objects.filter().exclude(system_specs=None)

        # get list of keypairs
        keypairs = KeyPair.objects.filter()
        authorized_keys = ""
        for keypair in keypairs:
            authorized_keys += keypair.value

        f = open("demofile", "w")
        f.write(authorized_keys)
        f.close()

        for server in servers:
            # here we need to write authorized_key file to server
            # then scp to server

            finger_print = configure_node(server)
            command = ("scp demofile %s@%s:~/.ssh/authorized_keys"
                       % (server.username, server.ip_address))
            print(command)
            os.system(command)

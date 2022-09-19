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

        for server in servers:
            server_user_keys = ServerUserKey.objects.filter(
                server=server)

            # get list of keypairs
            authorized_keys = ""
            for server_user_key in server_user_keys:
                authorized_keys += keypair.value

            f = open("demofile", "w")
            f.write(authorized_keys)
            f.close()

            finger_print = configure_node(server)
            # XXX how to do amerge or apend
            command = ("scp demofile %s@%s:~/.ssh/authorized_keys"
                       % (server.username, server.ip_address))
            print(command)
            os.system(command)

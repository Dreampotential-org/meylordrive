from tasks.models import Task, Server, ServerUserKey, KeyPair
import os
from django.core.management.base import BaseCommand


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
            # get the KeyPairs that are mapped to this server to build
            # .ssh/authorized_keys file
            print(authorized_keys)

            # here we need to write authorized_key file to server
            # then scp to server
            command = ("scp demofile %s@%s:~/.ssh/authorized_keys"
                       % (server.username, server.ip_address))
            print(command)
            os.system(command)

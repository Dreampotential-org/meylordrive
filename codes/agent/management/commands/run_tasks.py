from django.core.management.base import BaseCommand
from paramiko.client import SSHClient, AutoAddPolicy

from tasks.models import Task, Server


def run_job(server, task):
    print("Run job server: %s %s" % (server.username, server.ip_address))
    client = SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect(server.ip_address, username=server.username)
    stdin, stdout, stderr = client.exec_command('pwd; ls -alh')

    task.stdout = stdout.read().decode().strip()
    task.stderr = stderr.read().decode().strip()
    task.save()

    if task.stderr != "":
        raise Exception('There was an error pulling the runtime: {}'.format(task.stderr))
    print(task.stdout)
    client.close()


class Command(BaseCommand):
    help = 'run the tasks'

    def add_arguments(self, parser):
        # parser.add_argument('is_local', type=str)
        pass

    def handle(self, *args, **options):
        print("Start...")
        tasks = Task.objects.filter(status='not-active')
        print("Number of tasks to run: %s" % len(tasks))

        for task in tasks:
            print(task)
            server = Server.objects.filter().first()
            run_job(server, task)
        servers = Server.objects.filter()
        for server in servers:
            task = Task()
            run_job(server, task)

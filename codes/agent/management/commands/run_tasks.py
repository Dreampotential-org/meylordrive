from django.core.management.base import BaseCommand
from paramiko.client import SSHClient, AutoAddPolicy
import threading
import pprint

from tasks.models import Task, Server

def run_job(server, task):
    print("Run job server: %s %s" % (server.username, server.ip_address))
    client = SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect(server.ip_address, username=server.username,allow_agent=True) 
    #print(pprint.pprint(dir(client)))
    #client.channel.request_forward_agent()
    #stdin, stdout, stderr = client.exec_command('ls -alh /etc/apt/sources.list.d/')
    #stdin, stdout, stderr = client.exec_command('sudo rm -f /etc/apt/sources.list.d/buildkite-agent.list.save ; sudo cp /var/lib/dpkg/status-old /var/lib/dpkg/status ; sudo apt-get update -y')
    #stdin, stdout, stderr = client.exec_command('sudo cp /var/lib/dpkg/status-old /var/lib/dpkg/status')
    #stdin, stdout, stderr = client.exec_command('sudo mkdir /var/lib/dpkg ; sudo touch /var/lib/dpkg/status ; sudo apt-get update -y')
    stdin, stdout, stderr = client.exec_command('sudo apt-get update -y')

    task.stdout = stdout.read().decode().strip()
    task.stderr = stderr.read().decode().strip()
    task.save()

    if task.stderr != "":
        print("%s@%s" % (server.username, server.ip_address))
        print(task.stderr)
        #raise Exception('There was an error pulling the runtime: {}'.format(task.stderr))
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

        threads = []

        for task in tasks:
            print(task)
            server = Server.objects.filter().first()
            t = threading.Thread(target=run_job, args=(server, task))
            t.start()
            threads.append(t)
        servers = Server.objects.filter()
        for server in servers:
            task = Task()
            t = threading.Thread(target=run_job, args=(server, task))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

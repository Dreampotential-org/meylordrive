import time
import paramiko
import os
from django.core.management.base import BaseCommand
from paramiko.client import SSHClient, AutoAddPolicy
import threading
from pssh.clients import ParallelSSHClient

from pssh.config import HostConfig
import subprocess

from tasks.models import Task, Server


def run_job(server, task):
    print("Run job server: %s %s" % (server.username, server.ip_address))
    configure_node(server)
    client = SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect(server.ip_address, username=server.username, allow_agent=True)


def configure_node(server):
    ssh = paramiko.SSHClient()
    ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
    ssh.connect(server.ip_address, username=server.username)

    stdin, stdout, stderr = ssh.exec_command('rm -fr ~/.ssh/id_rsa')

    sftp = ssh.open_sftp()
    FILE = "/home/arosen/meylorCI/server-key"
    p = subprocess.Popen(["scp", FILE, "%s@%s:~/.ssh/id_rsa" % (
        server.username, server.ip_address)])

    print("Doing rm...")
    stdin, stdout, stderr = ssh.exec_command('rm -fr ~/django-zillow')
    # not sure we need to do this sleep here it is looking like
    time.sleep(2)
    print("Doing git clone...")
    stdin, stdout, stderr = ssh.exec_command(
        'git clone git@github.com:aaronorosen/django-zillow.git')

    # XXX why do we have to do this to make things work
    stdin, stdout, stderr = ssh.exec_command(
        'sudo touch /var/lib/dpkg/status')
    time.sleep(2)

    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command(
        'sudo apt-get update && apt-get upgrade -y')
    time.sleep(2)



    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command(
        'sudo rm -fr "rm -f /etc/apt/sources.list.d/buildkite-agent.list"')
    time.sleep(2)


    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command(
        'cd ~/django-zillow; COMMAND="kingtax"; DOWN_SCRIPT="./scripts/batch-down2.sh"; SCRIPT="./scripts/batch2.sh"; STATE="WA" bash scripts/batch2.sh')
    time.sleep(2)

    print(stdin)
    print(stdout)
    print(stderr)
    print(stdout.read().decode().strip())
    print(stderr.read().decode().strip())

    sftp.close()
    ssh.close()


class Command(BaseCommand):
    help = 'run the tasks'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        print("Start...")
        tasks = Task.objects.filter(status='not-active')
        print("Number of tasks to run: %s" % len(tasks))

        threads = []
        hosts = []
        host_config = []
        servers = Server.objects.filter()[1:2]
        for task in tasks:
            print(task)
            server = Server.objects.filter().first()
            t = threading.Thread(target=run_job, args=(server, task))
            t.start()
            threads.append(t)
        for server in servers:
            task = Task()
            t = threading.Thread(target=run_job, args=(server, task))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

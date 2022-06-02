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
    stdin, stdout, stderr = client.exec_command('sudo apt-get update -y')

    task.stdout = stdout.read().decode().strip()
    task.stderr = stderr.read().decode().strip()
    # task.save()
    print(task.stdout)

    if task.stderr != "":
        raise Exception('There was an error pulling the runtime: {}'.format(task.stderr))
    print("HERE is program output: %s" % task.stdout)
    client.close()


def configure_node(server):
    ssh = paramiko.SSHClient()
    ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
    ssh.connect(server.ip_address, username=server.username)

    stdin, stdout, stderr = ssh.exec_command('rm -fr ~/.ssh/id_rsa')

    sftp = ssh.open_sftp()
    FILE = "/home/arosen/meylorCI/server-key"
    p = subprocess.Popen(["scp", FILE, "%s@%s:~/.ssh/id_rsa" % (
        server.username, server.ip_address)])

    stdin, stdout, stderr = ssh.exec_command('rm -fr ~/django-zillow')
    # not sure we need to do this sleep here it is looking like
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command(
        'git clone git@github.com:aaronorosen/django-zillow.git')


    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command(
        'sudo rm -fr "rm -f /etc/apt/sources.list.d/buildkite-agent.list"')
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
        # parser.add_argument('is_local', type=str)
        pass

    def handle(self, *args, **options):
        print("Start...")
        tasks = Task.objects.filter(status='not-active')
        print("Number of tasks to run: %s" % len(tasks))

        threads = []
        hosts = []
        host_config = []
        servers = Server.objects.filter()
        # for server in servers:
        #    print(server.ip_address)
        #    hosts.append(server.ip_address)
        #    host_config.append(
        #        HostConfig(port=22, user='aaronoro',
        #                    private_key='server-key'),
        #        )

        # client = ParallelSSHClient(hosts, host_config=host_config)
        # output = client.run_command('cd ~; git clone git@github.com:aaronorosen/django-zillow.git')
        # output = client.run_command('uname')
        # client.join()

        # for host_output in output:
        #    for line in host_output.stdout:
        #        print(line)
        #    exit_code = host_output.exit_code
        #    print("Error exit code: %s" % exit_code)

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

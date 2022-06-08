import time
import paramiko
import os
from django.core.management.base import BaseCommand
from paramiko.client import SSHClient, AutoAddPolicy
import threading

from tasks.models import Task, Server

file1 = open("serverLogs.txt", "a")


def run_job(server, task):
    print("Run job server: %s %s" % (server.username, server.ip_address))
    configure_node(server)
    client = SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect(server.ip_address,
                   username=server.username, allow_agent=True)


def run_log_ssh_command(ssh, server, command):
    stdin, stdout, stderr = ssh.exec_command(command)
    file1.write(stderr.read().decode('utf-8') + "\n")
    print("COMMAND[%s]" % command)
    print("OUTPUT[%s]" % stdout.read())
    print("STDERROR[%s]" % stderr.read())


def configure_node(server):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_host_keys(os.path.expanduser(
        os.path.join("~", ".ssh", "known_hosts")))
    ssh.connect(server.ip_address, username=server.username)

    command = ("scp server-key %s@%s:~/"
               % (server.username, server.ip_address))
    output = os.system(command)
    print(output)
    time.sleep(10)

    run_log_ssh_command(ssh, server, "ssh-agent")
    run_log_ssh_command(ssh, server, "ssh-add server-key")
    run_log_ssh_command(ssh, server, "rm -fr ~/django-zillow")
    run_log_ssh_command(
        ssh, server, "ssh-keyscan github.com >> ~/.ssh/known_hosts")
    run_log_ssh_command(
        ssh, server,
        'git clone git@github.com:aaronorosen/django-zillow.git')
    run_log_ssh_command(ssh, server, 'sudo touch /var/lib/dpkg/status')
    run_log_ssh_command(
        ssh, server, 'sudo apt-get update && apt-get upgrade -y')
    run_log_ssh_command(
        ssh, server,
        'sudo rm -fr "rm -f /etc/apt/sources.list.d/buildkite-agent.list')
    run_log_ssh_command(
        ssh, server,
        'cd ~/django-zillow; COMMAND="kingtax"; DOWN_SCRIPT="./scripts/batch-down2.sh"; SCRIPT="./scripts/batch2.sh"; STATE="WA" sudo bash scripts/batch2.sh')
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
        servers = Server.objects.filter()[6:7]
        # for task in tasks:
        #    server = Server.objects.filter().first()
        #    t = threading.Thread(target=run_job, args=(server, task))
        #    t.start()
        #    threads.append(t)

        for server in servers:
            task = Task()
            t = threading.Thread(target=run_job, args=(server, task))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

from tasks.models import Task, Server, SystemSpecs
import paramiko
import os
from django.core.management.base import BaseCommand
from paramiko.client import SSHClient, AutoAddPolicy
import threading
import subprocess
temp = subprocess.Popen(["lscpu"], stdout=subprocess.PIPE)

file1 = open("serverLogs.txt", "a")

server_prints = {}


def run_job(server, task):
    print("Run job server: %s %s" % (server.username, server.ip_address))
    finger_print = configure_node(server)
    return finger_print


def run_log_ssh_command(ssh, server, command):
    stdin, stdout, stderr = ssh.exec_command(command)
    file1.write(stderr.read().decode('utf-8') + "\n")
    print("COMMAND[%s]" % command)
    print("OUTPUT[%s]" % stdout.read())
    print("STDERROR[%s]" % stderr.read())


def fingerprint_node(ssh, server):
    output = str(temp.communicate())
    dic = {}
    x = output.split("\n")[0].split("\\")
    for c, i in enumerate(x):
        if c < 25:
            if c == 0:
                dic[i[3:].split(":")[0]] = i[3:].split(":")[1].strip()
            if c != 0:
                dic[i[1:].split(":")[0]] = i[1:].split(":")[1].strip()
    server_prints[server.id] = dic


def configure_node(server):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_host_keys(os.path.expanduser(
        os.path.join("~", ".ssh", "known_hosts")))
    ssh.connect(server.ip_address, username=server.username, allow_agent=True)
    fingerprint_node(ssh, server)
    command = ("scp server-key %s@%s:~/"
               % (server.username, server.ip_address))
    output = os.system(command)

#    run_log_ssh_command(ssh, server, "ssh-agent")
#    run_log_ssh_command(ssh, server, "ssh-add server-key")
#    run_log_ssh_command(ssh, server, "rm -fr ~/django-zillow")
#    run_log_ssh_command(
#        ssh, server, "ssh-keyscan github.com >> ~/.ssh/known_hosts")


#    run_log_ssh_command(
#        ssh, server,
#        'git clone git@github.com:aaronorosen/django-zillow.git')
#    run_log_ssh_command(ssh, server, 'sudo touch /var/lib/dpkg/status')

#    run_log_ssh_command(
#        ssh, server, 'sudo apt-get update && apt-get upgrade -y')
#    run_log_ssh_command(
#        ssh, server,
#        'sudo rm -fr "rm -f /etc/apt/sources.list.d/buildkite-agent.list')
#    run_log_ssh_command(
#        ssh, server,
#        'cd ~/django-zillow; COMMAND="kingtax"; DOWN_SCRIPT="./scripts/batch-down2.sh"; SCRIPT="./scripts/batch2.sh"; STATE="WA" sudo bash scripts/batch2.sh')
    ssh.close()


def populate_system_specs(server, system_spec):
    server.system_specs.architecture = system_spec['Architecture']
    server.system_specs.cpu_op_modes = system_spec['Architecture']
    server.system_specs.byte_order = system_spec['Architecture']
    server.system_specs.address_sizes = system_spec['Architecture']
    server.system_specs.cpu_s = system_spec['Architecture']
    server.system_specs.on_line_cpu_s_list = system_spec['Architecture']
    server.system_specs.threads_per_core = system_spec['Architecture']
    server.system_specs.cores_per_socket = system_spec['Architecture']
    server.save()


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

        for server_print in server_prints.keys():
            populate_system_specs(server, server_prints[server_print])

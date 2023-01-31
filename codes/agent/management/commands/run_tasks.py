from tasks.models import Server, SystemSpecs, ProjectServiceLog, ProjectService
import paramiko
import os
from django.core.management.base import BaseCommand
import threading
from datetime import datetime
server_prints = {}


def configure_server(server):
    print("Run job server: %s %s" % (server.username, server.ip_address))
    finger_print = configure_node(server)
    # XXX this kills all containers on host so need to exclude containers
    # required for service to work.

    # XXX clear nodes to clean state.
    # run_log_ssh_command(make_ssh(server), "sudo bash kill-docker.sh")
    return finger_print


def run_project_command(server, project_command):
    project_service_log = ProjectServiceLog()
    # task_log.save()
    get_repo(make_ssh(server), project_command.repo, project_service_log)
    # think..
    # now run project_command.command.. which creates a task.


def start_project_service(project_service):

    # get list of servers and do one at a time to start...

    project_service_log = ProjectServiceLog()

    # start a task_log...
    for server in project_service.server_group.servers.all():
        run_project_service(server,  project_service, project_service_log)


def get_repo(ssh, repo, project_service_log):
    if repo is None:
        return
    print(repo)

    parsed_repo = repo.rsplit("/", 1)[1].split(".git")[0]
    response = run_log_ssh_command(
        ssh, f"cd {parsed_repo} && git pull", project_service_log)
    if response == 0:
        # run_log_ssh_command(ssh, "git pull", project_service_log)
        pass
    else:
        run_log_ssh_command(ssh, "git clone %s" % repo, project_service_log)
    # run_log_ssh_command(
    #     ssh, "rm -fr %s" % parsed_repo, project_service_log)


def run_log_ssh_command(ssh, command, project_service_log=None):
    print("COMMAND[%s]" % (command))
    stdin, stdout, stderr = ssh.exec_command(
        command)
    exit_status = stdout.channel.recv_exit_status()  # Blocking call
    stderr.channel.recv_exit_status()
    print("Exit status: %s" % exit_status)

    #  XXX https://github.com/mthenw/frontail
    path = 'logs'
    if not os.path.exists(path):
        os.makedirs(path)

    if project_service_log:
        # XXX someone needs to autocreate logs dir if not here..
        fileOut = open(f"./logs/{'out_'+str(project_service_log.id)}.txt", "a")
        fileErr = open(f"./logs/{'err_'+str(project_service_log.id)}.txt", "a")
    print("STARTING OF LOOP")
    if len(stdout.read()) > 0:
        for line in stdout.read().splitlines():
            print(line)
            if project_service_log:
                fileOut.write(str(line))
    print("STDERR")
    if len(stderr.read()) > 0:
        for line in stderr.read().splitlines():
            print(line)
            if project_service_log:
                fileErr.write(str(line))
    # file1.write(str(l) + "\n")
    # file1.close()
    print("ENDING OF LOOP")
    return int(exit_status)


def line_buffered(f):
    line_buf = ""
    while not f.channel.exit_status_ready():
        line_buf += str(f.read(1))
        if line_buf.endswith('\n'):
            yield line_buf
            line_buf = ''


def run_project_service(server, project_service, project_service_log):

    if project_service.repo is None:
        return

    project_service.command.status = "RUNNING"
    project_service.command.started_at = datetime.now()
    print("COMMAND[%s]" % project_service.command.cmd)

    repo_dir = project_service.repo

    fileOut = open(f"./logs/{'out_'+str(project_service_log.id)}.txt", "a")
    fileErr = open(f"./logs/{'err_'+str(project_service_log.id)}.txt", "a")

    repo_dir = project_service.repo.rsplit("/", 1)[1].split(".git")[0]
    ssh = make_ssh(server)

    print(repo_dir)

    stdin, stdout, stderr = ssh.exec_command(
        "cd %s && %s" % (repo_dir, project_service.command.cmd), get_pty=True,
        environment=project_service.command.environment_variable)

    while True:
        v = stdout.channel.recv(1024)
        if not v:
            break
        for line in v.splitlines():
            print(project_service.command.cmd, "==>", line)
            fileOut.write(str(line) + "\n")
    fileOut.close()
    stderr.channel.recv_exit_status()
    if len(stderr.read()) > 0:
        project_service.status = "FAILED"
        for line in stderr.read().splitlines():
            print(line)
            fileErr.write(str(line), "\n")
    else:
        project_service.status = "COMPLETED"
    project_service.command.last_finished_at = datetime.now()
    fileErr.close()


def fingerprint_node(ssh, server):
    stdin, stdout, stderr = ssh.exec_command("lscpu")
    memin, memout, memerr = ssh.exec_command("free -m")

    output = str(stdout.read())
    memoutput = str(memout.read())
    # print("OUTPUT", memoutput)
    memoutput = memoutput.split("\n")[0].split("\\n")
    totalMemory = memoutput[1].split(":")[1].strip()[0:5].strip()
    dic = {"total_memory": totalMemory}
    x = output.split("\n")[0].split("\\n")
    # print(x)
    for c, i in enumerate(x):
        if c < 22:
            if c == 0:
                dic[i[2:].split(":")[0]] = i[3:].split(":")[1].strip()
            if c != 0:
                dic[i.split(":")[0]] = i[1:].split(":")[1].strip()
    # print(dic)
    server_prints[server.id] = dic
    print(dic)


def make_ssh(server):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    sshkey = "/opt/server-key"

    try:
        if os.path.exists(sshkey):
            ssh.connect(server.ip_address, username=server.username,
                        key_filename=sshkey)
        else:
            ssh.connect(server.ip_address, username=server.username)
    except paramiko.ssh_exception.NoValidConnectionsError:
        server.error = True
        server.save()
        return
    return ssh


def configure_node(server):
    ssh = make_ssh(server)
    if not ssh:
        print("Not able to make ssh on %s" % server.ip_address)
        return

    # we get to this point with server it means we are able to
    # connect to it via ssh and can clear server error.
    server.error = False
    server.save()
    fingerprint_node(ssh, server)

    # XXX think about...
    # XXX make configurable for customer account or remove just for us.
    # command = ("scp server-key %s@%s:~/"
    #            % (server.username, server.ip_address))
    # os.system(command)

    command = ("scp kill-docker.sh %s@%s:~/"
               % (server.username, server.ip_address))
    os.system(command)
    ssh.close()


def populate_system_specs(server, system_spec):
    if not server.system_specs:
        server.system_specs = SystemSpecs()
    server.system_specs.architecture = system_spec['Architecture']
    server.system_specs.cpu_op_modes = system_spec['CPU op-mode(s)']
    server.system_specs.byte_order = system_spec['Byte Order']
    server.system_specs.cpu_s = int(system_spec['CPU(s)'])

    server.system_specs.on_line_cpu_s_list = system_spec['On-line CPU(s) list']
    server.system_specs.threads_per_core = system_spec['Thread(s) per core']
    server.system_specs.cores_per_socket = system_spec['Core(s) per socket']
    server.system_specs.sockets = system_spec['Socket(s)']
    server.system_specs.numa_nodes = system_spec.get('NUMA node(s)', 0)
    server.system_specs.vendor_id = system_spec['Vendor ID']
    server.system_specs.cpu_family = system_spec['CPU family']
    server.system_specs.model = system_spec['Model']
    server.system_specs.model_name = system_spec['Model name']
    server.system_specs.stepping = system_spec['Stepping']
    server.system_specs.cpu_mhz = system_spec.get('CPU MHz', 0)
    server.system_specs.bogo_mips = system_spec['BogoMIPS']
    server.system_specs.hypervisor_vendor = system_spec['Hypervisor vendor']
    server.system_specs.virtualization_type = system_spec.get(
        'Virtualization Type')
    server.system_specs.l1d_cache = system_spec['L1d cache']
    server.system_specs.l1i_cache = system_spec['L1i cache']
    server.system_specs.l2_cache = system_spec.get('L2 cache', 0)
    server.system_specs.l3_cache = system_spec.get('L3 cache', 0)
    server.system_specs.total_memory = system_spec['total_memory']
    server.system_specs.save()
    server.save()


def get_server():
    servers = Server.objects.filter(in_use=False).exclude(system_specs=None)
    if len(servers) == 0:
        print("No servers available")
        return False
    server_stats = {}
    for server in servers:
        server_stats[server.id] = server.system_specs.total_memory
    sortedData = {k: v for k, v in sorted(
        server_stats.items(), key=lambda item: item[1], reverse=True)}
    listData = list(sortedData.keys())
    return Server.objects.get(id=listData[0])


class Command(BaseCommand):
    help = 'run the tasks'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        print("Start...")

        # at the start we clear all severs that are in use.
        servers = Server.objects.filter().exclude(system_specs=None)
        for server in servers:
            server.in_use = False
            server.save()

        threads = []

        # get all servers and configure them
        servers = Server.objects.filter()
        for server in servers:
            t = threading.Thread(target=configure_server, args=(server))
            t.start()
            threads.append(t)

        # wait for all threads
        for t in threads:
            t.join()

        # populate server fingerprint in db
        for server_print in server_prints.keys():
            populate_system_specs(server, server_prints[server_print])

        # now we can progress tasks
        print("Running the tasks")
        # find list of status which do not have a status

        project_services = ProjectService.objects.filter()
        for project_service in project_services:
            start_project_service(project_service)

        # wait for complete
        for t in threads:
            t.join()

        # XXX should keep looping find more tasks that
        # have been created since...

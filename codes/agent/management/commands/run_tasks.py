from tasks.models import Server, SystemSpecs, ProjectServiceLog
from tasks.models import ProjectCommand, ProjectCommandLog
import paramiko
import os
from django.core.management.base import BaseCommand
import threading
from datetime import datetime
from utils.chirp import CHIRP
import logging
logging.getLogger("paramiko").setLevel(logging.WARNING)

server_prints = {}


def configure_server(server):
    CHIRP.info("Run job server: %s %s" % (server.username, server.ip_address))
    finger_print = configure_node(server)
    # XXX this kills all containers on host so need to exclude containers
    # required for service to work.

    # XXX clear nodes to clean state.
    # run_log_ssh_command(make_ssh(server), "sudo bash kill-docker.sh")
    return finger_print


def get_repo(ssh, repo, project_log):
    if repo is None:
        return
    CHIRP.info(repo)

    parsed_repo = repo.rsplit("/", 1)[1].split(".git")[0]
    response = run_log_ssh_command(
        ssh, f"cd {parsed_repo} && git pull origin main", project_log)
    if response == 0:
        # run_log_ssh_command(ssh, "git pull", project_service_log)
        pass
    else:
        run_log_ssh_command(
            ssh,
            "eval `ssh-agent`; ssh-add server-key; git checkout origin/main; GIT_SSH_COMMAND='ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no' git clone %s"
            % repo, project_log)


def run_log_ssh_command(ssh, command, project_log=None):
    CHIRP.info("COMMAND[%s]" % (command))
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()  # Blocking call
    stderr.channel.recv_exit_status()
    CHIRP.info("Exit status: %s" % exit_status)

    #  XXX https://github.com/mthenw/frontail
    path = 'logs'
    if not os.path.exists(path):
        os.makedirs(path)

    # XXX create logs dir if not here...
    fileOut = open(f"./logs/{'out_'+str(project_log.id)}.txt", "a")
    fileErr = open(f"./logs/{'err_'+str(project_log.id)}.txt", "a")
    CHIRP.info("STARTING OF LOOP")
    if len(stdout.read()) > 0:
        for line in stdout.read().splitlines():
            CHIRP.info(line)
            if project_log:
                fileOut.write(str(line))
    CHIRP.info("STDERR")
    if len(stderr.read()) > 0:
        for line in stderr.read().splitlines():
            CHIRP.info(line)
            if project_log:
                fileErr.write(str(line))
    # file1.write(str(l) + "\n")
    # file1.close()
    CHIRP.info("ENDING OF LOOP")
    return int(exit_status)


def line_buffered(f):
    line_buf = ""
    while not f.channel.exit_status_ready():
        line_buf += str(f.read(1))
        if line_buf.endswith('\n'):
            yield line_buf
            line_buf = ''


def run_project_command(server, project_command):
    project_command_log = ProjectCommandLog()
    project_command_log.project_command = project_command
    project_command_log.save()

    if project_command.project_service.repo is None:
        return

    CHIRP.info("server.ip_address=%s" % server.ip_address)
    get_repo(make_ssh(server), project_command.project_service.repo, project_command_log)

    project_command.project_service.status = "RUNNING"
    project_command.status = "RUNNING"
    project_command.started_at = datetime.now()
    project_command.save()
    project_command.project_service.save()
    CHIRP.info("Server: %s" % server.ip_address)
    CHIRP.info("COMMAND[%s]" % project_command.cmd)

    repo_dir = project_command.project_service.repo

    fileOut = open(f"./logs/{'out_'+str(project_command_log.id)}.txt", "a")
    fileErr = open(f"./logs/{'err_'+str(project_command_log.id)}.txt", "a")

    repo_dir = project_command.project_service.repo.rsplit("/", 1)[1].split(".git")[0]
    ssh = make_ssh(server)

    CHIRP.info(repo_dir)

    stdin, stdout, stderr = ssh.exec_command(
        "cd %s && %s" % (repo_dir,
                         project_command.cmd),
        get_pty=True,
        environment=project_command.environment_variable)

    while True:
        v = stdout.channel.recv(1024)
        if not v:
            break
        for line in v.splitlines():
            CHIRP.info('%s[%s] ==> %s'
                       % (server.ip_address, project_command.cmd[:8], line))
            fileOut.write(str(line) + "\n")
    fileOut.close()
    stderr.channel.recv_exit_status()
    if len(stderr.read()) > 0:
        project_command.project_service.status = "FAILED"
        for line in stderr.read().splitlines():
            CHIRP.info(line)
            fileErr.write(str(line), "\n")
    else:
        project_command.project_service.status = "COMPLETED"
    project_command.finished_at = datetime.now()
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
    CHIRP.info(dic)


def make_ssh(server):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()
    os.system("ssh-keyscan %s >> ~/.ssh/known_hosts" % server.ip_address)

    try:
        # if os.path.exists(sshkey):
        #    ssh.connect(server.ip_address, username=server.username,
        #                key_filename=sshkey)
        # else:
        CHIRP.info("Connecting %s@%s" % (server.username, server.ip_address))
        ssh.connect(server.ip_address, username=server.username)
    except paramiko.ssh_exception.NoValidConnectionsError as e:
        server.error = True
        server.save()
        raise e
    return ssh


def configure_node(server):
    ssh = make_ssh(server)
    if not ssh:
        CHIRP.info("Not able to make ssh on %s" % server.ip_address)
        return

    # we get to this point with server it means we are able to
    # connect to it via ssh and can clear server error.
    server.error = False
    server.save()
    fingerprint_node(ssh, server)

    # XXX think about...
    # XXX make configurable for customer account or remove just for us.
    command = ("scp server-key %s@%s:~/"
               % (server.username, server.ip_address))
    os.system(command)

    command = ("scp ~/.ssh/id_rsa %s@%s:~/server-key"
               % (server.username, server.ip_address))
    os.system(command)

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
    server.system_specs.hypervisor_vendor = system_spec.get(
        'Hypervisor vendor')
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
    servers = Server.objects.filter().exclude().order_by("?")
    return servers[0]
    if len(servers) == 0:
        CHIRP.info("No servers available")
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
        CHIRP.info("Start...")

        # at the start we clear all severs that are in use.
        servers = Server.objects.filter().exclude(system_specs=None)
        for server in servers:
            server.in_use = False
            server.save()

        threads = []

        # get all servers and configure them
        servers = Server.objects.filter()
        CHIRP.info("NUMBER OF SERVERS: %s" % len(servers))
        for server in servers:
            t = threading.Thread(target=configure_server, args=[server])
            t.start()
            threads.append(t)

        # wait for all threads
        for t in threads:
            t.join()

        # populate server fingerprint in db
        for server_print in server_prints.keys():
            populate_system_specs(server, server_prints[server_print])

        # now we can progress tasks
        CHIRP.info("Running the tasks")
        # find list of status which do not have a status

        project_commands = ProjectCommand.objects.filter()
        CHIRP.info("NUmber of commands: %s" % len(project_commands))
        for project_command in project_commands:
            server = get_server()
            CHIRP.info("START_command###")
            # start_project_service(project_service)
            t = threading.Thread(target=run_project_command,
                                 args=[server, project_command])
            t.start()
            threads.append(t)

        # wait for complete
        for t in threads:
            t.join()

        # XXX should keep looping find more tasks that
        # have been created since...

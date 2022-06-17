from tasks.models import Task, Server, SystemSpecs, TaskLog
import paramiko
import os
from django.core.management.base import BaseCommand
# from paramiko.client import SSHClient, AutoAddPolicy
import threading
import select
server_prints = {}


def run_job(server, task):
    return
    print("Run job server: %s %s" % (server.username, server.ip_address))
    finger_print = configure_node(server)
    return finger_print


def run_task(server, task, task_log):
    print("Run job server: %s %s" % (server.username, server.ip_address))
    get_repo(make_ssh(server), task.repo, task)
    run_log_ssh_task(make_ssh(server), server,
                     task, task_log, task.repo)


def get_repo(ssh, repo, task_log):
    if repo is None:
        return
    print(repo)
    # run_log_ssh_command(ssh, "rm -fr %s" % repo., task_log)
    run_log_ssh_command(
        ssh, "rm -fr %s" % repo.rsplit("/", 1)[1].split(".git")[0], task_log)
    run_log_ssh_command(ssh, "git clone %s" % repo, task_log)


def myexec(timeout, want_exitcode, stdin, stdout, stderr):
    # one channel per command
    #   stdin, stdout, stderr = ssh.exec_command(cmd)
    # get the shared channel for stdout/stderr/stdin
    channel = stdout.channel

    # we do not need stdin.
    stdin.close()
    # indicate that we're not going to write to that channel anymore
    channel.shutdown_write()

    # read stdout/stderr in order to prevent read block hangs
    stdout_chunks = []
    stdout_chunks.append(stdout.channel.recv(len(stdout.channel.in_buffer)))
    # chunked read to prevent stalls
    while not channel.closed or channel.recv_ready() or channel.recv_stderr_ready():
        # stop if channel was closed prematurely, and there is no data in the buffers.
        got_chunk = False
        readq, _, _ = select.select([stdout.channel], [], [], timeout)
        for c in readq:
            if c.recv_ready():
                stdout_chunks.append(stdout.channel.recv(len(c.in_buffer)))
                got_chunk = True
            if c.recv_stderr_ready():
                # make sure to read stderr to prevent stall
                stderr.channel.recv_stderr(len(c.in_stderr_buffer))
                got_chunk = True
        '''
      1) make sure that there are at least 2 cycles with no data in the input buffers in order to not exit too early (i.e. cat on a >200k file).
      2) if no data arrived in the last loop, check if we already received the exit code
      3) check if input buffers are empty
      4) exit the loop
      '''
        if not got_chunk \
                and stdout.channel.exit_status_ready() \
                and not stderr.channel.recv_stderr_ready() \
                and not stdout.channel.recv_ready():
            # indicate that we're not going to read from this channel anymore
            stdout.channel.shutdown_read()
            # close the channel
            stdout.channel.close()
            break    # exit as remote side is finished and our bufferes are empty

    # close all the pseudofiles
    stdout.close()
    stderr.close()

    if want_exitcode:
        # exit code is always ready at this point
        return (''.join(str(stdout_chunks)), stdout.channel.recv_exit_status())
    return ''.join(str(stdout_chunks))


def run_log_ssh_command(ssh, command, task_log):
    print("COMMAND[%s]" % command)
    stdin, stdout, stderr = ssh.exec_command(command)
    file1 = open("./logs/%s.txt" % task_log.id, "a")
    while True:
        if stdout.channel.recv_exit_status():
            break
        ot = myexec(10, True, stdin, stdout, stderr)

        print(ot)
        print("OUTPUT[%s] ResponseCode[%s]" % (ot[0], ot[1]))

        for line in ot[0]:
            print(line)
            file1.write(str(line) + "\n")
    file1.close()


def run_log_ssh_task(ssh, server, task, task_log, repo):
    if repo is None:
        return
    print("COMMAND[%s]" % task.command)
    file1 = open("./logs/%s.txt" % task_log.id, "a")

    repo_dir = repo.rsplit("/", 1)[1].split(".git")[0]
    stdin, stdout, stderr = ssh.exec_command(
        "cd %s && %s" % (repo_dir, task.command))

    file1.write(stderr.read().decode('utf-8') + "\n")
    print("OUTPUT[%s]" % stdout.read())
    print("STDERROR[%s]" % stderr.read())
    file1.close()


def fingerprint_node(ssh, server):
    # output = str(temp.communicate())
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
    ssh.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    ssh.connect(server.ip_address, username=server.username)
    return ssh


def configure_node(server):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())

    ssh.connect(server.ip_address, username=server.username)
    fingerprint_node(ssh, server)
    command = ("scp server-key %s@%s:~/"
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
    server.system_specs.numa_nodes = system_spec['NUMA node(s)']
    server.system_specs.vendor_id = system_spec['Vendor ID']
    server.system_specs.cpu_family = system_spec['CPU family']
    server.system_specs.model = system_spec['Model']
    server.system_specs.model_name = system_spec['Model name']
    server.system_specs.stepping = system_spec['Stepping']
    server.system_specs.cpu_mhz = system_spec['CPU MHz']
    server.system_specs.bogo_mips = system_spec['BogoMIPS']
    server.system_specs.hypervisor_vendor = system_spec['Hypervisor vendor']
    server.system_specs.virtualization_type = system_spec.get(
        'Virtualization Type')
    server.system_specs.l1d_cache = system_spec['L1d cache']
    server.system_specs.l1i_cache = system_spec['L1i cache']
    server.system_specs.l2_cache = system_spec['L2 cache']
    server.system_specs.l3_cache = system_spec['L3 cache']
    server.system_specs.total_memory = system_spec['total_memory']
    server.system_specs.save()
    server.save()


def get_server():
    servers = Server.objects.filter().exclude(system_specs=None)
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
        threads = []

        # get all servers and configure them
        servers = Server.objects.filter()
        for server in servers:
            task = Task()
            t = threading.Thread(target=run_job, args=(server, task))
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

        tasks = Task.objects.filter()
        print("Number of tasks to run: %s" % len(tasks))
        for task in tasks:
            # set task status to pending
            task.status = 'pending'
            task.save()

            server = get_server()
            if server == False:
                print("No servers available")
                os.exit(1)
            server.in_use = True
            server.save()

            task_log = TaskLog()
            task_log.task = task
            task_log.file_log = f"./logs/{task_log.id}.txt"
            task_log.save()

            # run the task
            t = threading.Thread(
                target=run_task, args=(server, task, task_log))
            t.start()
            threads.append(t)

        # wait for complete
        for t in threads:
            t.join()

        # XXX should keep looping find more tasks that
        # have been created since...

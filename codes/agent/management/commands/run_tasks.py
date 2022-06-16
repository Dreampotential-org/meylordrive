from tasks.models import Task, Server, SystemSpecs
import paramiko
import os
from django.core.management.base import BaseCommand
# from paramiko.client import SSHClient, AutoAddPolicy
import threading
server_prints = {}


def run_job(server, task):
    print("Run job server: %s %s" % (server.username, server.ip_address))
    finger_print = configure_node(server)
    return finger_print


def run_task(server, task, task_log):
    print("Run job server: %s %s" % (server.username, server.ip_address))
    get_repo(make_ssh(server), task.repo, task)
    run_log_ssh_task(make_ssh(server), server,
                     task, task_log, task.repo)


def get_repo(ssh, repo, task_log):
    if repo == None:
        return
    run_log_ssh_command(ssh, "git clone %s" % repo, task_log)
    run_log_ssh_command
    return
    # run_log_ssh_command(ssh, "sudo npm cache clean -f", task_log)
    # run_log_ssh_command(ssh, "sudo npm install -g n", task_log)
    # run_log_ssh_command(ssh, "sudo n stable", task_log)
    # run_log_ssh_command(ssh, "sudo npm i -g yarn", task_log)
    # run_log_ssh_command(ssh, "sudo apt install npm -y", task_log)


def run_log_ssh_command(ssh, command, task_log):
    print("COMMAND[%s]" % command)
    stdin, stdout, stderr = ssh.exec_command(command)
    while True:
        if stdout.channel.exit_status_ready():
            break
        line = stdout.readline()
        if len(line) == 0:
            break
        print(line)
    # XXX put in logs directory.
    file1 = open("./logs/%s.txt" % task_log.id, "a")
    file1.write(stderr.read().decode('utf-8') + "\n")
    print("OUTPUT[%s]" % stdout.read())
    print("STDERROR[%s]" % stderr.read())
    file1.close()


def run_log_ssh_task(ssh, server, task, task_log, repo):
    if repo == None:
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

    # ssh.load_host_keys(os.path.expanduser(
    #    os.path.join("~", ".ssh", "known_hosts")))
    ssh.connect(server.ip_address, username=server.username)
    fingerprint_node(ssh, server)
    command = ("scp server-key %s@%s:~/"
               % (server.username, server.ip_address))
    os.system(command)

    # run_log_ssh_command(
    #    ssh, server,
    #    'cd ~/django-zillow; COMMAND="kingtax"; DOWN_SCRIPT="./scripts/batch-down2.sh"; SCRIPT="./scripts/batch2.sh"; STATE="WA" sudo bash scripts/batch2.sh')
    ssh.close()


def populate_system_specs(server, system_spec):
    if not server.system_specs:
        server.system_specs = SystemSpecs()
    server.system_specs.architecture = system_spec['Architecture']
    server.system_specs.cpu_op_modes = system_spec['CPU op-mode(s)']
    server.system_specs.byte_order = system_spec['Byte Order']
    # server.system_specs.address_sizes = system_spec['Address sizes']
    server.system_specs.cpu_s = system_spec['CPU(s)']
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
    # server.system_specs.frequency_boost = system_spec['CPU max MHz']
    server.system_specs.cpu_mhz = system_spec['CPU MHz']
    # server.system_specs.cpu_max_mhz = system_spec['CPU max MHz']
    # server.system_specs.cpu_min_mhz = system_spec['CPU min MHz']
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


def get_available_servers():
    servers = Server.objects.filter(in_use=False)
    if len(servers) == 0:
        return False
    return servers


class Command(BaseCommand):
    help = 'run the tasks'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        print("Start...")

        threads = []

        # get all servers and configure them
        servers = Server.objects.filter()[:3]
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

            # find available server
            # XXX sort by system specs most cpus
            if get_available_servers() == False:
                continue
            dic = {}
            for i in server.values():
                dic[i['id']] = i
            powerful_server = {}
            for i in server.values():
                if(i["system_specs_id"] != None):
                    powerful_server[i["id"]] = SystemSpecs.objects.get(
                        id=i["system_specs_id"]).__dict__["cpu_s"]
            sortedData = {k: v for k, v in sorted(
                powerful_server.items(), key=lambda item: item[1], reverse=True)}
            listData = list(sortedData.keys())
            powerful_server = []
            for i in listData:
                powerful_server.append(dic[i])
            print(listData)
            server = Server.objects.get(id=listData[0])
            return
            if server == None:
                continue
            server.in_use = True
            server.save()

            task_log = Task()
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

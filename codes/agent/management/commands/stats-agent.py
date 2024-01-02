import datetime
import json
import time
import uuid
import re
import socket
import platform
import psutil
import asyncio
import threading
import websockets
import subprocess
from drive.models import Contact
# from codes.agent.management.commands.run_tasks import run_project_command
from utils.chirp import CHIRP


# from django.conf import settings

# settings.configure()


from drive.management.commands.google_voice_outbound import call_contact

# from codes.agent.management.commands.run_tasks import run_log_ssh_command


# from django.contrib.auth.models import User

def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


def get_stats():
    uname = platform.uname()
    swap = psutil.swap_memory()
    net_io = psutil.net_io_counters()
    try:
        disk_io = psutil.disk_io_counters()
    except ValueError:
        pass

    stats = {
        "agent_id": uuid.getnode(),
        "System": uname.system + str(datetime.datetime.utcnow()),
        "Node Name": uname.node,
        "Release": uname.release,
        "Version": uname.version,
        "Machine": uname.machine,
        "Processor": uname.processor,
        "Ip-Address": socket.gethostbyname(socket.gethostname()),
        "Mac-Address": {':'.join(re.findall('..', '%012x' % uuid.getnode()))},
        "TotalSwap": get_size(swap.total),
        "SwapFree": get_size(swap.free),
        "UsedSwap": get_size(swap.used),
        "SwapPercentage": swap.percent,
        "TotalBytesSent": get_size(net_io.bytes_sent),
        "TotalBytesReceived": get_size(net_io.bytes_recv),
        # "TotalRead": get_size(disk_io.read_bytes),
        # "TotalWrite": get_size(disk_io.write_bytes),
    }

    return stats


# Replace sets with lists in stats_json
def convert_sets_to_lists(obj):
    if isinstance(obj, set):
        return list(obj)
    elif isinstance(obj, dict):
        return {key: convert_sets_to_lists(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_sets_to_lists(item) for item in obj]
    else:
        return obj


async def send_health_data(websocket):
    try:
        while True:
            print("Task 1")
            stats_json = convert_sets_to_lists(get_stats())
            print(f"Stats Json: {stats_json}")

            # Send a message to the server
            await websocket.send(json.dumps({
                "message_type": "health_status",
                "message": stats_json
            }))

            await asyncio.sleep(5)
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"WebSocket connection closed with error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

async def main_loop(websocket, project_command):
    # Handle the received data here
    print("Final")
    print(f"Received data: {project_command}")
    if project_command:
        # start another thread
        t = threading.Thread(target=run_project_command, args=[project_command])
        t.start()
    else:
        print("comes here in else")
        time.sleep(10)


def do_command(command, task_id):
    process = subprocess.Popen([command],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    stdout, stderr
    fileOut = open(f"./logs/{'out_' + str(task_id)}.txt", "a")
    fileErr = open(f"./logs/{'err_' + str(task_id)}.txt", "a")

    # for future task is build api server aroud log file
    if len(stdout.read()) > 0:
        for line in stdout.read().splitlines():
            CHIRP.info(line)
            if task_id:
                fileOut.write(str(line))
    CHIRP.info("STDERR")
    if len(stderr.read()) > 0:
        for line in stderr.read().splitlines():
            CHIRP.info(line)
            if task_id:
                fileErr.write(str(line))


def get_repo(task):
    if task is None:
        return
    CHIRP.info(task)

    parsed_repo = repo.rsplit("/", 1)[1].split(".git")[0]
    # XXX need to call subprocesss or os.system
    response = run_log_ssh_command(
        ssh, f"cd {parsed_repo} && git pull origin main", project_log)
    if response == 0:
        # run_log_ssh_command(ssh, "git pull", project_service_log)
        pass
    else:
        run_log_ssh_command(
            ssh,
            "eval `ssh-agent`; ssh-add id_rsa; git checkout origin/main; git clone %s" % repo, project_log)


def run_project_command(project_command):
    get_repo(task.repo)

    project_command.project_service.status = "RUNNING"
    project_command.status = "RUNNING"
    project_command.started_at = datetime.now()
    CHIRP.info("Server: %s" % server.ip_address)
    CHIRP.info("COMMAND[%s]" % project_command.cmd)

    repo_dir = project_command.project_service.repo

    fileOut = open(f"./logs/{'out_' + str(project_command.id)}.txt", "a")
    fileErr = open(f"./logs/{'err_' + str(project_command.id)}.txt", "a")

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


async def receive_task_data(websocket):
    while True:
        data = await websocket.recv()
        json_data = json.loads(data)
        # Handle the received data here
        print(f"Received data: {data}")
        contact = Contact.objects.filter(id=1).first()
        import threading
        t = threading.Thread(target=call_contact, args=[contact])
        t.start()
        threads.append(t)
        # Check if the received data contains contact details
        if "message_type" in json_data and json_data["message_type"] == "contact_details":
            # Extract the contact phone number
            contact_phone = json_data.get("message", {}).get("contact_phone", None)




async def main():
    SERVER = 'ws://127.0.0.1:8021'
    api_key = '7ee9132d-c84e-449e-9f91-50997e65f6cf'

    uri = f"{SERVER}/ws/contact/?api_key={api_key}&agent_id={uuid.getnode()}"
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected Over {uri}")

            # Start the tasks to send and receive data
            tasks = [
                send_health_data(websocket),
                receive_task_data(websocket),
            ]

            results = await asyncio.gather(*tasks)
            command_data = results[1]

            # Start another task
            tasks_two = [
                main_loop(websocket, command_data),
            ]

            await asyncio.gather(*tasks_two)

    except websockets.exceptions.WebSocketException as e:
        print(f"WebSocket connection error: {e}")


from django.core.management.base import BaseCommand
import requests


class Command(BaseCommand):
    help = 'run the tasks'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        asyncio.run(main())

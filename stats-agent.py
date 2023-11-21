import datetime
import json
import time
import uuid
import re
import sys
import socket
import platform
import psutil
import asyncio
import threading
import websockets
import subprocess
# from codes.agent.management.commands.run_tasks import run_project_command
from codes.utils.chirp import CHIRP


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


async def send_health_data(websocket, username):
    while True:
        print("Task 1")
        stats_json = convert_sets_to_lists(get_stats())
        # Add 'username' key to the JSON data
        data = {'message': 'health_data', 'username': username, 'stats': stats_json}
        print(f"Stats Json: {stats_json}")
        stats_string = json.dumps(data)
        # Send a message to the server
        await websocket.send(stats_string)
        await asyncio.sleep(5)


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
    received_data = []
    while True:
        data = await websocket.recv()
        json_data = json.loads(data)
        # Handle the received data here
        print(f"Received data: {data}")
        # Add your processing logic for received data here
        received_data.append(json_data)
        return received_data
    
# async def receive_task_data(websocket):
#     received_data = []
#     while True:
#         data = await websocket.recv()
#         json_data = json.loads(data)
#         # Handle the received data here
#         print(f"Received data: {data}")
#         # Add your processing logic for received data here
#         received_data.append(json_data)

import asyncio
import websockets
import json

# async def send_data():
#     uri = "ws://127.0.0.1:8000/ws/chat_1/?api_key=7ee9132d-c84e-449e-9f91-506cf"
#     async with websockets.connect(uri) as websocket:
#         data = {'message': 'Your message here', 'other_key': 'other_value'}
#         await websocket.send(json.dumps(data))

# asyncio.get_event_loop().run_until_complete(send_data())

async def main(room_slug,username):
    # XXX we need to get from cmd arg or conf file
    api_key = '7ee9132d-c84e-449e-9f91-506cf'
    uri = f"ws://127.0.0.1:8000/ws/{room_slug}/?api_key={api_key}"

    try:
        async with websockets.connect(uri) as websocket:
            # WebSocket connection is open
            print(f"Connected Over {uri}")

            # start some threads
            # Start the tasks to send and receive data
            tasks = [
                asyncio.create_task(send_health_data(websocket, username)),
                asyncio.create_task(receive_task_data(websocket)),
            ]

            results = await asyncio.gather(*tasks)
            command_data = results[1]

            tasks_two = [
                asyncio.create_task(main_loop(websocket, command_data)),
            ]

            await asyncio.gather(*tasks_two)

    except websockets.exceptions.WebSocketException as e:
        print(f"WebSocket connection error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python stats-agent.py <room_slug> <username>")
        sys.exit(1)

    room_slug = sys.argv[1]
    username = sys.argv[2]

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(room_slug, username))

import datetime
import json
import time
import uuid
import re
import socket
import platform
import psutil
import asyncio
import websockets

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
    disk_io = psutil.disk_io_counters()

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
        "TotalRead": get_size(disk_io.read_bytes),
        "TotalWrite": get_size(disk_io.write_bytes),
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


async def main():
    uri = "ws://127.0.0.1:8000/ws/chat/"
    async with websockets.connect(uri) as websocket:
        # WebSocket connection is open
        print(f"Connected Over {uri}")
        while True:
            stats_json = convert_sets_to_lists(get_stats())
            print(f"Stats Json: {stats_json}")
            stats_string = json.dumps(stats_json)
            # Send a message to the server
            await websocket.send(stats_string)
            time.sleep(5)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())

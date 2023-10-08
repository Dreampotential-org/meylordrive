import uuid
import re
import socket
import platform
import psutil

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

    stats = {
        "System": uname.system,
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
        #"TotalRead": get_size(disk_io.read_bytes),
        #"TotalWrite": get_size(disk_io.write_bytes),
    }

    print(stats)



get_stats()

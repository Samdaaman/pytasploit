import os
import pwd

LOCAL_IP = os.environ['PYTERPRETER_LOCAL_IP']
WEBSERVER_PORT = 1337
INSTANCE_ID: str = None
USERNAME = pwd.getpwuid(os.getuid()).pw_name

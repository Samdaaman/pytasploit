import os
import pwd

LOCAL_IP = '127.0.0.1'
WEBSERVER_PORT = 1337
INSTANCE_ID: str = None
USERNAME = pwd.getpwuid(os.getuid()).pw_name

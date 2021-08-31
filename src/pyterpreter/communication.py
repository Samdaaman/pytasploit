import urllib.error
import urllib.request
from queue import SimpleQueue
from threading import Thread
import time

from core.message import Message

from pyterpreter import config

config.messages_to_send = SimpleQueue()
config.messages_received = SimpleQueue()

_base_url = f'http://{config.LOCAL_IP}:{config.WEBSERVER_PORT}'


def initialise():
    def receive_messages_forever():
        while True:
            time.sleep(1)
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
                    config.messages_received.put(Message.from_string(data))

    def send_messages_forever():
        while True:
            message = config.messages_to_send.get()
            urllib.request.urlopen(urllib.request.Request(f'{_base_url}/instances/{config.INSTANCE_ID}', message.to_string().encode(), {'Content-Type': 'text/plain'}))

    create_instance()
    Thread(target=receive_messages_forever, daemon=True).start()
    Thread(target=send_messages_forever, daemon=True).start()
    print('Communication initialised')


def create_instance():
    create_instance_res = urllib.request.urlopen(urllib.request.Request(f'{_base_url}/instances', f'{config.USERNAME}'.encode(), {'Content-Type': 'text/plain'}))
    instance_id = create_instance_res.read().decode()
    assert instance_id is not None and len(instance_id) > 0
    config.INSTANCE_ID = instance_id
    print(f'Instance created at {instance_id}')

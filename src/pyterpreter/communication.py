import urllib.request
from queue import SimpleQueue
from threading import Thread
import time

from core.message import Message

from pyterpreter import config

_messages_to_send: 'SimpleQueue[Message]' = SimpleQueue()
messages_received: 'SimpleQueue[Message]' = SimpleQueue()

_base_url = f'http://{config.LOCAL_IP}:{config.WEBSERVER_PORT}'


def initialise():
    def receive_messages_forever():
        while True:
            poll_messages = urllib.request.urlopen(f'{_base_url}/instances/{config.INSTANCE_ID}')
            data = poll_messages.read().decode()
            if len(data) > 0:
                messages_received.put(Message.from_string(data))
            else:
                time.sleep(3)

    def send_messages_forever():
        while True:
            message = _messages_to_send.get()
            urllib.request.urlopen(f'{_base_url}/instances/{config.INSTANCE_ID}', message.to_string().encode())

    create_instance = urllib.request.urlopen(f'{_base_url}/instances', b'')
    instance_id = create_instance.read().decode()
    assert instance_id is not None and len(instance_id) > 0
    config.INSTANCE_ID = instance_id

    Thread(target=receive_messages_forever, daemon=True).start()
    Thread(target=send_messages_forever, daemon=True).start()
    print('comms initialised')

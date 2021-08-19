from queue import SimpleQueue
from threading import Thread
from typing import Tuple, Union

from core.message import Message

from instance import Instance

_messages_received: 'SimpleQueue[Tuple[Instance, Message]]' = SimpleQueue()


def add_message(instance: Instance, message: Message):
    _messages_received.put((instance, message))


def process_new_messages_forever(blocking=False):
    if not blocking:
        Thread(target=process_new_messages_forever, args=(True,), daemon=True).start()
    else:
        while True:
            instance, message = _messages_received.get()
            # TODO
            print(f'Message received from {instance.instance_id}: {message}')

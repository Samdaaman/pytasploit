from threading import Thread

from core.message import *

import config
from instance import Instance


def process_new_messages_forever(blocking=False):
    if not blocking:
        Thread(target=process_new_messages_forever, args=(True,), daemon=True).start()
    else:
        while True:
            instance, message = config.all_messages_received.get()  # type: Instance, Message

            if isinstance(message, PingResponse):
                continue

            # TODO
            print(f'Message received from {instance.instance_id}: {message}')

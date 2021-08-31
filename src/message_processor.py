from threading import Thread

from core.message import Message, MESSAGE_PURPOSE

import config
from instance import Instance


def process_new_messages_forever(blocking=False):
    if not blocking:
        Thread(target=process_new_messages_forever, args=(True,), daemon=True).start()
    else:
        while True:
            instance, message = config.all_messages_received.get()  # type: Instance, Message

            if message.purpose == MESSAGE_PURPOSE.PING:
                continue

            # TODO
            print(f'Message received from {instance.instance_id}: {message}')

from queue import SimpleQueue
import time
from typing import Tuple

from core.message import Message

import config


class Instance:
    instance_id: str
    username: str
    last_message_received: float
    messages_to_send: 'SimpleQueue[Message]'

    def __init__(self, instance_id, username: str):
        self.instance_id = instance_id
        self.username = username
        self.last_message_received = time.perf_counter()
        self.messages_to_send = SimpleQueue()

    def messages_received_put(self, message: Message) -> None:
        self.last_message_received = time.perf_counter()
        config.all_messages_received.put((self, message))

    def is_root(self):
        return self.username == 'root'

    def __str__(self):
        return f'{self.username}@{self.instance_id}'

    def execute_command(self, name: str, params: dict) -> dict:
        pass




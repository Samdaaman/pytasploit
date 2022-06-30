from queue import Queue
import time

from core.message import Message


class Instance:
    instance_id: str
    username: str
    last_message_received: float
    messages_to_send: 'Queue[Message]'

    def __init__(self, instance_id, username: str):
        self.instance_id = instance_id
        self.username = username
        self.last_message_received = time.perf_counter()
        self.messages_to_send = Queue()

    def is_root(self):
        return self.username == 'root'

    def __str__(self):
        return f'{self.username}@{self.instance_id}'

    def execute_command(self, name: str, params: dict) -> dict:
        pass




from queue import SimpleQueue

from core.message import Message


class Instance:
    instance_id: str
    username: str
    messages_to_send: 'SimpleQueue[Message]'
    messages_received: 'SimpleQueue[Message]'

    def __init__(self, instance_id, username: str):
        self.instance_id = instance_id
        self.username = username
        self.messages_to_send = SimpleQueue()
        self.messages_received = SimpleQueue()

    def is_root(self):
        return self.username == 'root'

    def __str__(self):
        return f'{self.username}@{self.instance_id}'
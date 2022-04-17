from threading import Thread

from core.command import CommandRequest
from core.message import Message, MessageTypes

from pyterpreter import config


def process_messages_forever(blocking=False):
    if blocking:
        while True:
            message = config.messages_received.get()
            _process_message(message)
    else:
        Thread(target=process_messages_forever, args=(True,), daemon=True).start()


def _process_message(message: Message):
    if message.message_type == MessageTypes.COMMAND_REQUEST:
        config.commands_to_process.put(CommandRequest.from_json(message.data))

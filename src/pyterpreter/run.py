from core.message import Message

from pyterpreter import communication, message_processor


def run():
    communication.initialise()
    print('Herro der')

    message_processor.process_messages_forever(communication.messages_received)

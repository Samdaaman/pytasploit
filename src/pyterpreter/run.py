from pyterpreter import communication, message_processor
from pyterpreter import config
import os


def run():
    print(os.environ)
    print(f'username is {config.USERNAME}')
    communication.initialise()
    message_processor.process_messages_forever(communication.messages_received)

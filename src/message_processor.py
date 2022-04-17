from base64 import b64decode
from threading import Thread

from core.event import EventTypes, Event
from core.message import *

import config
from instance import Instance
from my_logging import Logger


logger = Logger('MSG_PROCESSOR')


def process_new_messages_forever(blocking=False):
    if not blocking:
        Thread(target=process_new_messages_forever, args=(True,), daemon=True).start()
    else:
        while True:
            instance, message = config.all_messages_received.get()

            if message.message_type == MessageTypes.EVENT:
                event = Event.from_json(message.data)
                if event.event_type == EventTypes.RUN_FILE_FINISH:
                    command_uid = event.data['command_uid']  # type: str
                    exit_code = event.data['exit_code']  # type: int
                    output = b64decode(event.data['output_b64'])
                    filename = config.run_file_commands_in_progress.pop(command_uid)
                    output_file = f'../output/{instance.username}_{filename}_{command_uid}'
                    logger.info(f'{filename} file exited with code: {exit_code} and outputted {len(output)} bytes to {output_file}')
                    with open(output_file, 'wb') as fh:
                        fh.write(output)

            # TODO
            # print(f'Message received from {instance.instance_id}: {message}')

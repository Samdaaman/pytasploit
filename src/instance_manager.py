import random
import string
from threading import Lock, Thread
import time
from typing import Callable, List, Optional, Tuple

from core.command import CommandTypes, CommandRequest
from core.message import *

from instance import Instance

_lock = Lock()
_instances: List[Instance] = []
on_instances_update: Callable[[Tuple[Instance], Optional[Instance]], None]


def create_instance(username: str = 'unknown') -> Instance:
    instance = Instance(
        ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16)),
        username
    )
    with _lock:
        _instances.append(instance)
        on_instances_update(tuple(_instances), instance)

    return instance


def get_by_id(instance_id: str) -> Optional[Instance]:
    with _lock:
        for instance in _instances:
            if instance.instance_id == instance_id:
                return instance


def remove_instance(instance):
    with _lock:
        if instance in _instances:
            _instances.remove(instance)
            on_instances_update(tuple(_instances), instance)


def ping_instances_forever(blocking=False):
    ping_delay = 3

    if not blocking:
        return Thread(target=ping_instances_forever, args=[True], daemon=True).start()

    while True:
        with _lock:
            for instance in _instances.copy():
                if instance.last_message_received < time.perf_counter() - 3 * ping_delay:
                    _instances.remove(instance)
                    on_instances_update(tuple(_instances), instance)
                else:
                    message = Message(MessageTypes.COMMAND_REQUEST, CommandRequest(CommandTypes.PING).to_json())
                    instance.messages_to_send.put(message)

        time.sleep(ping_delay)

#
# def get_all() -> List[Instance]:
#     with _lock:
#         return _instances.copy()

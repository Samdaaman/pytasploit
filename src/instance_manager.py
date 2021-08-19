from threading import Lock
import random
import string
from typing import Callable, List, Optional, Tuple

from core.message import Message, MESSAGE_PURPOSE

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

#
# def get_all() -> List[Instance]:
#     with _lock:
#         return _instances.copy()

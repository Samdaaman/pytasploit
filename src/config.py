from queue import SimpleQueue
from typing import Dict, Tuple

from core.message import Message

from instance import Instance

all_messages_received: 'SimpleQueue[Tuple[Instance, Message]]' = SimpleQueue()
run_file_commands_in_progress: Dict[str, str] = {}

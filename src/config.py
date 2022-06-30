from queue import Queue
from typing import Dict, Tuple

from core.message import Message

from instance import Instance

all_messages_received: 'Queue[Tuple[Instance, Message]]' = Queue()
run_file_commands_in_progress: Dict[str, str] = {}

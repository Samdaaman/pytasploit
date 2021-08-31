from queue import SimpleQueue

all_messages_received: 'SimpleQueue[tuple]' = SimpleQueue()
'''type is SimpleQueue[Tuple[Instance, Message]] or a queue of (instance, message)'s'''

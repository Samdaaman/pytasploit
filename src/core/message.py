from typing import List, Optional
import random
import string
from dataclasses import dataclass
import json
import inspect


class MESSAGE_PURPOSE:
    PING = 'PING'
    OPEN_SHELL = 'OPEN_SHELL'
    RUN_SCRIPT = 'RUN_SCRIPT'
    STEALTH = 'STEALTH'
    SELF_DESTRUCT = 'SELF_DESTRUCT'


class Message:
    def encode(self):
        json_obj = self.__dict__.copy()
        json_obj['__class__'] = self.__class__.__name__
        json_str = json.dumps(json_obj, indent=2)
        return json_str

    @staticmethod
    def decode(json_str: str):
        json_obj = json.loads(json_str)
        assert isinstance(json_obj, dict), 'json_obj must be a dict'

        message_class_name = json_obj.get('__class__')
        del json_obj['__class__']
        assert message_class_name is not None, 'message_class_name cannot be none'

        message_class = globals().get(message_class_name)
        if (message_class is None) or (not inspect.isclass(message_class)):
            raise Exception(f'Constructor for {message_class_name} is missing')

        # constructor_kwargs = {}
        # post_construct_attributes = json_obj.copy()
        # for key in message_class.__dataclass_fields__.keys():
        #     constructor_kwargs[key] = json_obj[key]
        #     del post_construct_attributes[key]

        message_obj = message_class(**json_obj)
        # for key in post_construct_attributes:
        #     setattr(message_obj, key, post_construct_attributes[key])
        return message_obj


class Request(Message):
    request_id: str

    def __init__(self, request_id: Optional[str] = None):
        super().__init__()
        self.request_id = request_id if request_id else ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))


@dataclass
class Response(Message):
    request_id: str

    def __init__(self, request_id: str):
        self.request_id = request_id


class PingRequest(Request):
    pass


class PingResponse(Response):
    pass


class RunScriptRequest(Request):
    script_name: str
    script_args: List[str]

    def __init__(self, script_name: str, script_args: List[str], **kwargs):
        super().__init__(**kwargs)
        self.script_name = script_name
        self.script_args = script_args


class OpenReverseShellRequest(Request):
    port: int

    def __init__(self, port: int, **kwargs):
        super().__init__(**kwargs)
        self.port = port


class SelfDestructRequest(Request):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class GoStealthyRequest(Request):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

import json


class MessageTypes:
    COMMAND_REQUEST = "COMMAND_REQUEST"
    COMMAND_RESPONSE = "COMMAND_RESPONSE"
    COMMAND_RESPONSE_ERROR = "COMMAND_RESPONSE_ERROR"
    EVENT = "EVENT"


class Message:
    def __init__(self, message_type: str, data: dict):
        self.message_type = message_type
        self.data = data

    @staticmethod
    def decode(json_str: str) -> 'Message':
        message = json.loads(json_str)
        return Message(
            message_type=message["message_type"],
            data=message["data"],
        )

    def encode(self) -> str:
        return json.dumps({
            "message_type": self.message_type,
            "data": self.data,
        })

    def __str__(self):
        return "{}: {}".format(self.message_type, json.dumps(self.data, indent=2))

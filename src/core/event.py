from typing import Optional


class EventTypes:
    RUN_FILE_FINISH = "RUN_FILE_FINISH"


class Event:
    def __init__(self, event_type: str, data: Optional[dict] = None):
        self.event_type = event_type
        self.data = data if data is not None else {}

    def to_json(self) -> dict:
        return {
            "event_type": self.event_type,
            "data": self.data,
        }

    @staticmethod
    def from_json(data: dict) -> 'Event':
        return Event(
            event_type=data["event_type"],
            data=data["data"],
        )

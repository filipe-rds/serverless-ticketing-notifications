from typing import Any

from ticketstream.shared.exceptions import InfrastructureException


class InMemoryEventRepository:
    def __init__(self):
        self.events = []

    def findById(self, event_id: str) -> dict[str, Any]:
        for event in self.events:
            if event["event_id"] == event_id:
                return event

        raise InfrastructureException(f"Event {event_id} not found")

    def findAll(self) -> list[dict[str, Any]]:
        return self.events

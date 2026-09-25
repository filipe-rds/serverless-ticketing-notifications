from uuid import UUID

from ticketstream.ticketing.domain.entities.event import Event


class InMemoryEventRepository:
    def __init__(self, events: list[Event] | None = None) -> None:
        self._events: list[Event] = events if events is not None else []

    def find_by_id(self, event_id: UUID) -> Event | None:
        for event in self._events:
            if event.event_id == event_id:
                return event

        return None

    def find_all(self) -> list[Event]:
        return list(self._events)
